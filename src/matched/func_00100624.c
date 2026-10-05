/* func_00100624 : 空壳栈帧包装（o2_tail，编译档 -O2）
 * 由 routebjp/tools/auto_match_wrapper.py 生成；objdiff 100% 后纳入 hybrid。
 * 语义：本函数只做参数整理后调用 iopsmem_8（延迟槽/nop 由模板决定）。 */
extern void iopsmem_8();

void func_00100624() { iopsmem_8(); }
