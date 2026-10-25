/* iopldfl_4 @ 0x002c4b30 (32 B) : call func_002c4908 with a 16-byte stack buffer and a zero 5th arg
 *
 * The retail function is a normal call, not a tail call; see config/source_flags.tsv.
 */
extern void func_002c4908(int, int, int, void *, long long);

void iopldfl_4(int a, int b, int c)
{
  char buf[0x10];
  func_002c4908(a, b, c, buf, 0);
}
