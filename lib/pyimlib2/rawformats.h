unsigned int get_raw_bytes_size(char *format);
unsigned char *get_raw_bytes(char *format, unsigned char *dstbuf);
unsigned char *convert_raw_rgba_bytes(char *from_format, char *to_format,
                  unsigned char *from_buf, unsigned char *to_buf,
                  int w, int h);
void init_rgb2yuv_tables();
