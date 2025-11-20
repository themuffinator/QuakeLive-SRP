/*
=============
fs_imports.h

Filesystem import table shared across native syscall shims.
=============
*/

#ifndef QLR_FS_IMPORTS_H
#define QLR_FS_IMPORTS_H

typedef struct qlr_fs_imports_s {
	int (*fopen_file_by_mode)(const char *path, int *handle, int mode);
	int (*fopen_web_file_read)(const char *path, int *handle, char *resolved, int resolved_len);
	int (*filelength)(int handle);
	void (*read)(void *buffer, int len, int handle);
	int (*write)(const void *buffer, int len, int handle);
	void (*fclose_file)(int handle);
	int (*get_file_list)(const char *path, const char *extension, char *listbuf, int bufsize);
	int (*seek)(int handle, long offset, int origin);
	char *(*build_os_path)(const char *base, const char *game, const char *qpath);
	const char *(*loaded_pak_checksums)(void);
	const char *(*loaded_pak_pure_checksums)(void);
	const char *(*referenced_pak_checksums)(void);
	const char *(*referenced_pak_pure_checksums)(void);
} qlr_fs_imports_t;

extern const qlr_fs_imports_t qlr_fs_imports;

#endif /* QLR_FS_IMPORTS_H */
