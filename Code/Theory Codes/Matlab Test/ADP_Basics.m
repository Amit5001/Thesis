m = 4 ;%kg
A = [0 1; 0 0];
B= [0;1];

Q = [1 0 ; 0 1];
R = 1;

[K_lqr, P_lqr, E_lqr] = lqr(A,B,Q,R);


K_i = 0.4 * K_lqr;
P_old = zeros(size(A));
K_kleinman = [];
P_kleinman = [];

for i= 1:100
    A_bar = A-B*K_i;
    Q_bar = Q_lqr +K_i'*R_lqr*K_i;

    P_i = lyap(A_bar', Q_bar);
    K_i = inv(R)*B'*P_i;

    if norm(P_i -P_old) < 0.01
        K_kleinman =[K_kleinman, K_i];
        break
    end

    P_old = P_i;
    K_kleinman = [K_kleinman, K_i'];
end

