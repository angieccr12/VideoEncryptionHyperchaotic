clear all; close all; clc;

% Parámetros del sistema (NHS)
a = 2; b = 2; c = 0.5; d = 14.5;

% Retardos
tau1 = 0.12;
tau2 = 0.25;
tau3 = 0.38;

% Integración
h = 0.001;
N = 50000;

% Retardos en pasos
nTau1 = round(tau1/h);
nTau2 = round(tau2/h);
nTau3 = round(tau3/h);

% Condición inicial e historial
X = zeros(4, N+1);
X(:,1) = [1;1;1;1];
t = zeros(1, N+1);

for n = 2:max([nTau1,nTau2,nTau3])+1
    X(:,n) = X(:,1);
end

% Parámetros Lyapunov
m = 4;
V = eye(m);
LE = zeros(m,1);
renorm = 10;
t_lyap = 0;

LE_hist = zeros(m, floor(N/renorm));
k_lyap = 1;

% Integración RK4 + Lyapunov
for n = max([nTau1,nTau2,nTau3])+1 : N

    k1 = h * fSistema4D_delay(X,n,nTau1,nTau2,nTau3,a,b,c,d);
    k2 = h * fSistema4D_delay(X,n,nTau1,nTau2,nTau3,a,b,c,d,0.5*k1);
    k3 = h * fSistema4D_delay(X,n,nTau1,nTau2,nTau3,a,b,c,d,0.5*k2);
    k4 = h * fSistema4D_delay(X,n,nTau1,nTau2,nTau3,a,b,c,d,k3);

    X(:,n+1) = X(:,n) + (k1+2*k2+2*k3+k4)/6;
    t(n+1) = n*h;

    % ---- Lyapunov ----
    J = jacobiano4D(X(:,n),a,b,c);
    V = V + h*J*V;

    if mod(n,renorm)==0
        [Q,R] = qr(V);
        V = Q;
        LE = LE + log(abs(diag(R)));
        t_lyap = t_lyap + renorm*h;

        LE_hist(:,k_lyap) = LE/t_lyap;
        k_lyap = k_lyap + 1;
    end
end

% Coeficientes finales
lambda = LE / t_lyap;

% ANALISIS AUTOMATICO DE CAOS (COMMAND WINDOW)
tol = 1e-3;

num_pos = sum(lambda > tol);
num_zero = sum(abs(lambda) <= tol);
sum_lambda = sum(lambda);

fprintf('        ANALISIS DE CAOS DEL SISTEMA\n');
fprintf('Coeficientes de Lyapunov:\n');
for i = 1:length(lambda)
    fprintf('  lambda_%d = %+9.6f\n', i, lambda(i));
end

fprintf('\nResumen dinámico:\n');

if num_pos == 0
    fprintf('  - Sistema NO caótico\n');
elseif num_pos == 1
    fprintf('  - Sistema CAOTICO (1 exponente positivo)\n');
else
    fprintf('  - Sistema HIPERCAOTICO (%d exponentes positivos)\n', num_pos);
end

if num_zero >= 1
    fprintf('  - Exponente cercano a cero → dinámica tipo flujo\n');
end

if sum_lambda < 0
    fprintf('  - Sistema DISIPATIVO (suma de Lyapunov < 0)\n');
else
    fprintf('  - Sistema NO disipativo\n');
end

% Estados
x = X(1,:); y = X(2,:); z = X(3,:); w = X(4,:);

% Atractor 3D
figure;
subplot(2,2,1), plot3(x,y,z,'k'), grid on, title('(x,y,z)')
subplot(2,2,2), plot3(x,y,w,'b'), grid on, title('(x,y,w)')
subplot(2,2,3), plot3(x,z,w,'r'), grid on, title('(x,z,w)')
subplot(2,2,4), plot3(y,z,w,'m'), grid on, title('(y,z,w)')
sgtitle('Atractor del sistema 4D con retardos')

% Evolución temporal
figure;
subplot(4,1,1), plot(t,x,'k'), ylabel('x(t)'), grid on
subplot(4,1,2), plot(t,y,'b'), ylabel('y(t)'), grid on
subplot(4,1,3), plot(t,z,'r'), ylabel('z(t)'), grid on
subplot(4,1,4), plot(t,w,'m'), ylabel('w(t)'), xlabel('Tiempo'), grid on
sgtitle('Evolución temporal del sistema')

% Convergencia de Lyapunov
time_lyap = (1:size(LE_hist,2))*renorm*h;

figure;
plot(time_lyap,LE_hist(1,:),'k','LineWidth',1.5); hold on
plot(time_lyap,LE_hist(2,:),'r','LineWidth',1.5)
plot(time_lyap,LE_hist(3,:),'b','LineWidth',1.5)
plot(time_lyap,LE_hist(4,:),'m','LineWidth',1.5)
yline(0,'--')
xlabel('Tiempo')
ylabel('\lambda_i(t)')
title('Convergencia de los coeficientes de Lyapunov')
legend('\lambda_1','\lambda_2','\lambda_3','\lambda_4')
grid on

%% DIAGRAMA DE BIFURCACION CON SECCION DE POINCARE
fprintf('\n========================================\n');
fprintf('CALCULANDO DIAGRAMA DE BIFURCACION...\n');
fprintf('========================================\n');

% Parámetro a variar: d (más sensible para visualizar bifurcaciones)
d_min = 1.0;
d_max = 16.0;
d_steps = 1000;  % Alta resolución ideal 600
 
d_values = linspace(d_min, d_max, d_steps);

% Configuración optimizada
N_trans = 25000;  % Más transiente
N_max = 60000;    % Más iteraciones
N_samples = 150;  % Muestras por valor de parámetro ideal 80
h_bif = 0.005;

% Almacenamiento
bifurcation_data = [];
d_data = [];

fprintf('Parámetros:\n');
fprintf('  - Rango de d: [%.1f, %.1f]\n', d_min, d_max);
fprintf('  - Resolución: %d puntos\n', d_steps);
fprintf('  - Muestras por punto: %d\n\n', N_samples);

for idx = 1:length(d_values)
    d_current = d_values(idx);
    
    % Inicialización
    X_bif = zeros(4, N_max);
    X_bif(:,1) = [1; 1; 1; 1];
    
    % Buffers de retardo
    nTau1_bif = round(tau1/h_bif);
    nTau2_bif = round(tau2/h_bif);
    nTau3_bif = round(tau3/h_bif);
    max_delay = max([nTau1_bif, nTau2_bif, nTau3_bif]);
    
    for n = 2:max_delay+1
        X_bif(:,n) = X_bif(:,1);
    end
    
    % Integración RK4 con captura de Poincaré
    poincare_x = [];
    n_samples = 0;
    z_threshold = 0.0;  % Umbral ajustado
    
    for n = max_delay+1 : N_max-1
        % RK4
        k1 = h_bif * fSistema4D_delay(X_bif,n,nTau1_bif,nTau2_bif,nTau3_bif,a,b,c,d_current);
        k2 = h_bif * fSistema4D_delay(X_bif,n,nTau1_bif,nTau2_bif,nTau3_bif,a,b,c,d_current,0.5*k1);
        k3 = h_bif * fSistema4D_delay(X_bif,n,nTau1_bif,nTau2_bif,nTau3_bif,a,b,c,d_current,0.5*k2);
        k4 = h_bif * fSistema4D_delay(X_bif,n,nTau1_bif,nTau2_bif,nTau3_bif,a,b,c,d_current,k3);
        
        X_bif(:,n+1) = X_bif(:,n) + (k1+2*k2+2*k3+k4)/6;
        
        % Sección de Poincaré después del transiente
        if n > N_trans
            z_prev = X_bif(3, n);
            z_curr = X_bif(3, n+1);
            
            % Cruce ascendente de z = z_threshold
            if z_prev <= z_threshold && z_curr > z_threshold
                % Interpolación lineal
                alpha = (z_threshold - z_prev) / (z_curr - z_prev);
                x_cross = X_bif(1,n) + alpha * (X_bif(1,n+1) - X_bif(1,n));
                
                poincare_x = [poincare_x; x_cross];
                n_samples = n_samples + 1;
                
                if n_samples >= N_samples
                    break;
                end
            end
        end
    end
    
    % Almacenar resultados
    if ~isempty(poincare_x)
        bifurcation_data = [bifurcation_data; poincare_x];
        d_data = [d_data; ones(length(poincare_x),1) * d_current];
    end
    
    % Progreso
    if mod(idx, 50) == 0
        fprintf('Progreso: %d/%d (%.1f%%) | d=%.2f | Puntos: %d\n', ...
            idx, d_steps, 100*idx/d_steps, d_current, length(poincare_x));
    end
end

fprintf('\n✓ Completado.\n');
fprintf('  Total de puntos: %d\n\n', length(bifurcation_data));

% Visualización optimizada
figure('Position', [100, 100, 1000, 500], 'Color', 'white');
plot(d_data, bifurcation_data, '.', 'Color', [0.1 0.1 0.6], 'MarkerSize', 0.5);
xlabel('Parámetro d', 'FontSize', 13, 'FontWeight', 'bold');
ylabel('Sección de Poincaré: x cuando z = 7 ↑', 'FontSize', 13, 'FontWeight', 'bold');

title('Diagrama de Bifurcación - Sistema Hipercaótico con Retardos', 'FontSize', 15, 'FontWeight', 'bold');
grid on;
xlim([d_min d_max]);
set(gca, 'FontSize', 11);

% Marcar el valor usado en el análisis
hold on;
xline(d, 'r-', 'LineWidth', 2.5, 'Alpha', 0.7);
text(d, min(bifurcation_data), sprintf(' d = %.1f', d), ...
    'FontSize', 11, 'Color', 'r', 'FontWeight', 'bold', ...
    'VerticalAlignment', 'bottom');
hold off;

% SISTEMA CON RETARDOS
function dX = fSistema4D_delay(X,n,nTau1,nTau2,nTau3,a,b,c,d,offset)
if nargin<10, offset=[0;0;0;0]; end
Xtemp = X(:,n)+offset;

x = Xtemp(1); y = Xtemp(2);
z = Xtemp(3); w = Xtemp(4);

x_tau1 = X(1,n-nTau1);
y_tau2 = X(2,n-nTau2);
z_tau3 = X(3,n-nTau3);

dx = -a*x_tau1 - b*y*z;
dy = -x + c*y_tau2 + c*w;
dz = d - y^2 - z_tau3;
dw = x - w;

dX = [dx;dy;dz;dw];
end

% JACOBIANO
function J = jacobiano4D(X,a,b,c)

x = X(1); y = X(2); z = X(3); w = X(4);

J = zeros(4,4);

J(1,2) = -b*z;
J(1,3) = -b*y;

J(2,1) = -1;
J(2,4) = c;

J(3,2) = -2*y;

J(4,1) = 1;
J(4,4) = -1;
end
