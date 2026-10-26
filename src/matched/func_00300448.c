/* func_00300448 @ 0x00300448 (28 B, CRI) : return *(int *)(p + i*0x44 + 0x1FAC) != 0 */
int func_00300448(char *p, int i)
{
  p += i * 0x44;
  return *(int *)(p + 0x1FAC) != 0;
}
