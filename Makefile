CC=gcc
CFLAGS=-Wall -g -std=c99 -O2 -D_FILE_OFFSET_BITS=64
LIBS=`pkg-config --libs gmime-2.0` -luuid
INCS=`pkg-config --cflags gmime-2.0`

recmail: recmail.c
	$(CC) $(CFLAGS) -o recmail recmail.c ${LIBS} ${INCS}

clean:
	rm -f recmail *.o
