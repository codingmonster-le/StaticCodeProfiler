# StaticCodeProfiler

Input:  c/c++/java files

Output: classification of statements based on their operators and data types of variables

Example output: test.cpp

%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Statement classification based on computation

17 – the number of arithmetic

13 – the number of conditions (including loop conditions)

9 – the number of loops

10 – the number of goto, break, continue, return

74 – the number of calls

Statement classification based on data types

171 – the number of statements with only scalar (int, long, char, Boolean, short) data type

0 – the number of statements with float point – single precision

94 – the number of statements with double

0 – the number of statements with containers (stack, array, list, queue)

127 – the number of statements with user defined data types
%%%%%%%%%%%%%%%%%%%%%%%%%%%%

Setup: Download srcml http://www.srcml.org/ to a folder named src2srcml

Run: staticcodeprofiler.py test.cpp
