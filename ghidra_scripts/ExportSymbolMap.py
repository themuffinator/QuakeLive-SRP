# Quake Live symbol map exporter
#@author OpenAI
#@category QuakeLive/Exports
#@menupath Tools.QuakeLive.Export Symbol Map
#@toolbar ql_symbol_map.png

"""Export a structured JSON manifest of symbols, string references, and relocations.

The script is intentionally self contained so it can run either in the GUI or via
`analyzeHeadless`.  When running headless, provide the output directory and the
optional alias JSON via script arguments, e.g.::

    analyzeHeadless <project> <project_name> -process client.x86 \
        -postScript ExportSymbolMap.py /path/to/references/symbol-maps \
        /path/to/references/analysis/quakelive_symbol_aliases.json

The alias file should contain a mapping per binary like::

    {
        "client": {"sub_401230": "CL_Frame"}
    }

Any raw names that are not present in the alias map will be emitted with a
consistent prefix so that they can be grepped easily for follow-up triage.
"""

import json
import os
import datetime

from ghidra.app.script import GhidraScript
from ghidra.program.model.symbol import SymbolType
from ghidra.program.model.data import StringDataType, TerminatedStringDataType, UnicodeDataType


class ExportSymbolMap(GhidraScript):

    def run(self):
        program = self.currentProgram
        if program is None:
            self.printerr("No program is active; aborting")
            return

        binary_name = os.path.basename(program.getExecutablePath())
        binary_root, _ = os.path.splitext(binary_name)
        binary_key = binary_root.lower()

        args = list(self.getScriptArgs())
        output_dir = None
        alias_path = None
        if len(args) > 0:
            output_dir = args[0]
        if len(args) > 1:
            alias_path = args[1]

        if not output_dir:
            dir_obj = self.askDirectory("Select output directory", "Select")
            if dir_obj is None:
                self.printerr("No output directory selected")
                return
            output_dir = dir_obj.getAbsolutePath()

        if alias_path is None:
            alias_candidate = os.path.join(os.path.dirname(output_dir), "analysis", "quakelive_symbol_aliases.json")
            if os.path.exists(alias_candidate):
                alias_path = alias_candidate

        alias_map = self._load_aliases(alias_path, binary_key)
        unresolved_prefix = "UNRESOLVED_%s" % binary_key.upper()

        function_entries, string_refs = self._collect_functions(program, alias_map, unresolved_prefix)
        string_entries = self._collect_strings(program, string_refs, unresolved_prefix)
        reloc_entries = self._collect_relocations(program)

        payload = {
            "schema_version": 1,
            "binary": binary_key,
            "input_path": program.getExecutablePath(),
            "generated_at": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
            "normalization": {
                "alias_source": alias_path,
                "unresolved_prefix": unresolved_prefix
            },
            "functions": function_entries,
            "strings": string_entries,
            "relocations": reloc_entries,
            "stats": {
                "function_total": len(function_entries),
                "function_matched": len([f for f in function_entries if f.get("status") == "matched"]),
                "string_total": len(string_entries),
                "string_resolved": len([s for s in string_entries if s.get("status") == "matched"]),
                "relocation_total": len(reloc_entries)
            }
        }

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_path = os.path.join(output_dir, "%s.json" % binary_key)
        with open(output_path, "w") as handle:
            json.dump(payload, handle, indent=2, sort_keys=False)

        self.println("Wrote symbol manifest to %s" % output_path)

    # ------------------------------------------------------------------

    def _load_aliases(self, alias_path, binary_key):
        if not alias_path or not os.path.exists(alias_path):
            return {}
        try:
            with open(alias_path, "r") as handle:
                data = json.load(handle)
        except Exception as err:
            self.printerr("Failed to parse alias map %s: %s" % (alias_path, err))
            return {}
        return data.get(binary_key, {}) or {}

    def _collect_functions(self, program, alias_map, unresolved_prefix):
        listing = program.getListing()
        function_manager = program.getFunctionManager()
        functions = []
        string_refs = {}

        func_iter = function_manager.getFunctions(True)
        while func_iter.hasNext():
            func = func_iter.next()
            entry = func.getEntryPoint()
            raw_name = func.getName()
            normalized = alias_map.get(raw_name)
            status = "matched"
            if not normalized:
                normalized = "%s_func_%08X" % (unresolved_prefix, entry.getOffset())
                status = "unresolved"

            references = set()
            instr_iter = listing.getInstructions(func.getBody(), True)
            while instr_iter.hasNext():
                instr = instr_iter.next()
                for ref in instr.getReferencesFrom():
                    target = ref.getToAddress()
                    data = listing.getDataAt(target)
                    if data and self._is_string_data(data):
                        references.add(target)

            reference_list = [self._format_address(addr) for addr in sorted(references)]
            string_refs[self._format_address(entry)] = reference_list

            reloc_offsets = []
            for ref in func.getSymbol().getReferences():
                if ref.isExternalReference():
                    reloc_offsets.append(self._format_address(ref.getFromAddress()))

            signature = None
            if func.hasNoReturn():
                signature = "void %s(void) /* noreturn */" % normalized
            elif func.getPrototypeString(False, False) is not None:
                signature = func.getPrototypeString(True, True)

            functions.append({
                "address": self._format_address(entry),
                "raw_name": raw_name,
                "normalized_name": normalized,
                "status": status,
                "signature": signature,
                "string_refs": reference_list,
                "relocation_refs": sorted(reloc_offsets),
                "comment": func.getComment() or ""
            })

        return functions, string_refs

    def _collect_strings(self, program, function_string_refs, unresolved_prefix):
        listing = program.getListing()
        string_entries = {}

        data_iter = listing.getDefinedData(True)
        while data_iter.hasNext():
            data = data_iter.next()
            if not self._is_string_data(data):
                continue
            addr = data.getAddress()
            addr_key = self._format_address(addr)
            value = data.getDefaultValueRepresentation()
            label = self._string_symbol(addr)
            status = "matched"
            if not label:
                label = "%s_str_%08X" % (unresolved_prefix, addr.getOffset())
                status = "unresolved"

            refs = []
            ref_iter = data.getReferenceIteratorTo()
            while ref_iter.hasNext():
                ref = ref_iter.next()
                func = program.getFunctionManager().getFunctionContaining(ref.getFromAddress())
                if func:
                    refs.append(self._format_address(func.getEntryPoint()))

            if addr_key in function_string_refs:
                refs = list(set(refs) | set(function_string_refs[addr_key]))

            string_entries[addr_key] = {
                "address": addr_key,
                "value": value,
                "xref_functions": sorted(set(refs)),
                "normalized_label": label,
                "status": status
            }

        # Ensure we emit entries for any strings referenced but not defined (e.g. external)
        for func_addr, refs in function_string_refs.items():
            for ref in refs:
                if ref not in string_entries:
                    string_entries[ref] = {
                        "address": ref,
                        "value": None,
                        "xref_functions": [func_addr],
                        "normalized_label": "%s_str_%s" % (unresolved_prefix, ref.replace("0x", "")),
                        "status": "unresolved"
                    }

        return [string_entries[key] for key in sorted(string_entries.keys())]

    def _collect_relocations(self, program):
        relocation_table = program.getRelocationTable()
        iterator = relocation_table.getRelocations()
        relocations = []
        while iterator.hasNext():
            reloc = iterator.next()
            relocations.append({
                "offset": self._format_address(reloc.getAddress()),
                "type": reloc.getTypeName(),
                "symbol": reloc.getSymbolName()
            })
        return sorted(relocations, key=lambda item: item["offset"])

    def _is_string_data(self, data):
        datatype = data.getDataType()
        if isinstance(datatype, (StringDataType, TerminatedStringDataType, UnicodeDataType)):
            return True
        name = datatype.getName().lower()
        if "string" in name:
            return True
        return False

    def _string_symbol(self, address):
        symbol_table = self.currentProgram.getSymbolTable()
        symbols = symbol_table.getSymbols(address)
        for symbol in symbols:
            if symbol.getSymbolType() in (SymbolType.DATA, SymbolType.LABEL):
                return symbol.getName()
        return None

    def _format_address(self, address):
        if hasattr(address, "getOffset"):
            return "0x%08X" % address.getOffset()
        if isinstance(address, (int, long)):
            return "0x%08X" % address
        return str(address)


if __name__ == "__main__":
    ExportSymbolMap().run()
