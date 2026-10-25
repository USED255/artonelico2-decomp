/* func_00344320 @ 0x00344320 (16 B) : sign-extend the 32-bit word at p+0x8 */
int func_00344320(unsigned int *p)
{
  return (int)(((unsigned long long)p[2] << 32) >> 32);
}
