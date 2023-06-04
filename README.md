# SILK
![](https://img.shields.io/hexpm/l/plug?style=flat-square)

SILK is a hybrid fuzzing tool guided by branch constraints, which mainly consists of two parts: AFL-SILK and coordinator.

## AFL-SILK

 AFL-SILK explores paths in descending order of difficulty. The installation process of AFL-SILK is simple because it is the same as that of AFL。 We also have an independent version of [AFL-SILK](https://github.com/White-Mouse/AFL-SILK) that differs from the current version in that it does not transfer branch execution information to shared memory.

## coordinator

The following describes what each file does

    -*read_data* Read branch execution information from shared memory

    -*seed_eval.py* Count the number of times each constraint is solved and calculate the stuck probability (*stuck_pr*)
    
    -*run_qsym_afl.py* Call the QSYM interface, QSYM can be replaced by other concolic executors
