/* func_00335140 @ 0x00335140 (32 B, CRI) : sign-extend (p[5] << 11) truncated to 32 bits */
int func_00335140(int *p)
{
  return (int)(((long long)p[5] << 11) & 0xFFFFFFFFLL);
}
