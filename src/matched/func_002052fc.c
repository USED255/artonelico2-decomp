typedef unsigned long ulong;
typedef unsigned int undefined4;
extern void func_00204fa8(ulong, undefined4);
void func_002052fc(ulong param_1)
{
  int new_var;
  undefined4 uVar1;
  uVar1 = 6;
  if (2 < param_1)
  {
    new_var = 5;
    uVar1 = new_var;
  }
  if (new_var)
  {
    func_00204fa8(param_1, uVar1);
    return;
  }
  else
  {
    func_00204fa8(param_1, uVar1);
    return;
  }
}
