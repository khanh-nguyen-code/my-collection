function [x] = solve_l1(A, b)
  % forming a linear programming problem
  [m, n] = size(A);
  bub = zeros(2*n, 1);
  Aub = nan(2*n, 2*n);
  Aub(1:n, 1:n) = +eye(n);
  Aub(1:n, n+1:n+n) = -eye(n);
  Aub(n+1:n+n, 1:n) = -eye(n);
  Aub(n+1:n+n, n+1:n+n) = -eye(n);
  
  beq = b;
  Aeq = nan(m, 2*n);
  Aeq(:, 1:n) = A;
  Aeq(:, n+1:n+n) = 0;
  
  c = nan(2*n, 1);
  c(1:n) = 0;
  c(n+1:n+n) = 1;
  % solve
  x_ = linprog(c, Aub, bub, Aeq, beq);
  x = x_(1:n);
end


