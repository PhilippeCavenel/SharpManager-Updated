CC ?= cc
all: bas2img bin2wav wav2bin

bas2img: bas2img_600.c 
	$(CC) -Wall -o bas2img bas2img_600.c
bin2wav: bin2wav_200b.c
	$(CC) -Wall -o bin2wav bin2wav_200b.c
wav2bin: wav2bin_200a.c
	$(CC) -Wall -o wav2bin wav2bin_200a.c
	 
clean:
	rm -f bas2img bin2wav wav2bin
