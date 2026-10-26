extern void eepatch_30(int);
int glue_9(int a, int b){ if (a == 1) eepatch_30(b); return 0; }
