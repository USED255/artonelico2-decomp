/* func_00344310 @ 0x00344310 (16 B) : sign-extend the 32-bit word at p+0xC */
int func_00344310(unsigned int *p)
{
  return (int)(((unsigned long long)p[3] << 32) >> 32);
}
