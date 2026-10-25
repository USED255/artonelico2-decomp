/* iopldfl_6 @ 0x002c4b50 (28 B) : call func_002c4908 with a zero 5th argument
 *
 * The retail function is a normal call, not a tail call, so this source carries
 * `-fno-optimize-sibling-calls` in config/source_flags.tsv.
 */
extern void func_002c4908(int, int, int, int, long long);

void iopldfl_6(int a, int b, int c, int d)
{
  func_002c4908(a, b, c, d, 0);
}
