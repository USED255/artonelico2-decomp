/* func_003424b8 @ 0x003424b8 (32 B, CRI) : write a word to p[0..3] in big-endian byte order */
void func_003424b8(char *p, unsigned int v)
{
  p[0] = (char)(v >> 24);
  p[1] = (char)(v >> 16);
  p[2] = (char)(v >> 8);
  p[3] = (char)v;
}
