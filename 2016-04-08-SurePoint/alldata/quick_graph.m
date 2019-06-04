%close all;
load processed.data; f = processed;
f(:,1) = f(:,1) - f(1,1);

figure(1);
%hold off;
plot(f(:,1), f(:,2), f(:,1), f(:,5), f(:,1), f(:,3), f(:,1), f(:,6), f(:,1), f(:,4), f(:,1), f(:,7), f(:,1), f(:,8)-10, 'o')
legend('PH x', 'MO x', 'PH y', 'MO y', 'PH z', 'MO z', 'error-10');

figure(2);

scatter3(f(:,2), f(:,3), f(:,4),'filled')
%hold on;
%scatter3(f(:,5), f(:,6), f(:,7),'filled','color','green')
