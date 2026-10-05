/* func_001e3ce0 : 空壳栈帧包装（o1_jal，编译档 -O1）
 * 由 routebjp/tools/auto_match_wrapper.py 生成；objdiff 100% 后纳入 hybrid。
 * 语义：本函数只做参数整理后调用 func_001e3b74（延迟槽/nop 由模板决定）。 */
extern void func_001e3b74();

void func_001e3ce0(int a, int b, int c) { func_001e3b74(a, b, c, 0); }
