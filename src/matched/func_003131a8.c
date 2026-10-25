/* func_003131a8 @ 0x003131a8 (20 B) : write three bytes at p+0x14..p+0x16 */
void func_003131a8(char *p, int a, int b, int c)
{
  p += 0x14;
  p[0] = (char)a;
  p[1] = (char)b;
  p[2] = (char)c;
}
