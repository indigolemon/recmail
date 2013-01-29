/*
 * recmail.c
 *
 * Copyright (C) 2013		PCCL
 * 				Andrew Clayton <andrew@pccl.info>
 *
 * Released under the GNU General Public License version 2.
 * See COPYING
 */

#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <time.h>
#include <limits.h>

#include <uuid/uuid.h>

#include <gmime/gmime.h>

#include <glib.h>

#define MD_BASE_DIR	"/data/maildata"
#define BUF_SIZE	4096

/*
 * Process a MIME part of the mail message
 */
static void process_part(GMimeObject *part)
{
	GMimeStream *stream;
	GMimeDataWrapper *content;
	char file[NAME_MAX + 1];
	int fd;
	static int npart = 0;
	FILE *fp;

	fp = fopen("00INDEX", "a");
	snprintf(file, sizeof(file), "part-%03d.obj", npart++);
	fprintf(fp, "%s\t%s\n", file, (char *)g_mime_part_get_filename(
				(GMimePart *)part));
	fclose(fp);

	fd = open(file, O_CREAT | O_WRONLY | O_TRUNC, 0666);
	stream = g_mime_stream_fs_new(fd);
	content = g_mime_part_get_content_object((GMimePart *)part);
	g_mime_data_wrapper_write_to_stream(content, stream);
	g_mime_stream_flush(stream);
	close(fd);

	g_object_unref(content);
	g_object_unref(stream);
}

/*
 * Process a mail message, passed on by sendmail
 */
static void process_message(void)
{
	GMimeMessage *message;
	GMimeStream *stream;
	GMimeParser *parser;
	int fd;

	g_mime_init(0);

	fd = open("maildata.dat", O_RDONLY);
	stream = g_mime_stream_fs_new(fd);
	parser = g_mime_parser_new_with_stream(stream);
	message = g_mime_parser_construct_message(parser);
	g_mime_message_foreach_part(message, (GMimePartFunc)process_part, NULL);

	close(fd);
	g_object_unref(stream);
	g_object_unref(parser);
	g_object_unref(message);

	g_mime_shutdown();
}

int main(int argc, char **argv)
{
	int fd;
	int err;
	ssize_t bytes_read;
	ssize_t bytes_wrote;
	time_t t = time(NULL);
	struct tm *tm = localtime(&t);
	char buf[BUF_SIZE];
	char maildir[PATH_MAX];
	char uuid_s[37];	/* 36 char UUID + '\0' */
	const char *whoami;
	uuid_t uuid;

	umask(0007);

	whoami = (strstr(argv[0], "/")) ? strrchr(argv[0], '/') + 1 : argv[0];

	uuid_generate(uuid);
	uuid_unparse(uuid, uuid_s);

	snprintf(maildir, PATH_MAX, "%s/%s/%d/%02d/%02d/%s",
			(argc == 2) ? argv[1] : MD_BASE_DIR, whoami,
			tm->tm_year + 1900, tm->tm_mon + 1, tm->tm_mday,
			uuid_s);

	g_mkdir_with_parents(maildir, 0777);
	err = chdir(maildir);
	if (err == -1)
		exit(EXIT_FAILURE);

	/* Store file passed in to stdin */
	fd = open("maildata.dat", O_CREAT | O_WRONLY | O_TRUNC | O_EXCL, 0666);
	if (fd == -1)
		exit(EXIT_FAILURE);
	do {
		bytes_read = read(STDIN_FILENO, &buf, BUF_SIZE);
		bytes_wrote = write(fd, buf, bytes_read);
		if (bytes_wrote != bytes_read)
			exit(EXIT_FAILURE);
	} while (bytes_read > 0);
	close(fd);

	process_message();

	exit(EXIT_SUCCESS);
}
