n = 1000;
m = 200;

A = rand(m, n);
b = rand(m, 1);
tic;
x = solve_l1(A, b);
toc;
fprintf("constraint: %f\n", sum(abs(A*x-b)));
fprintf("norm: %f\n", sum(abs(x)));
fprintf("sparsity: %f\n", sum(x ==0) / n);