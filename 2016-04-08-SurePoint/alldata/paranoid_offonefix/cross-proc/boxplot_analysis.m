%load onept_13.2b
%spatio_nt = onept_13
load onept_14.2b
spatio_nt = onept_14

spatio_nt_medians = zeros(27,1);
for ii=1:27
	spatio_nt_medians(ii) = median(spatio_nt(~isnan(spatio_nt(:,ii)),ii));
end
[~, spatio_nt_medians_sort] = sort(spatio_nt_medians);
grp = [];
errors = [];
for ii=1:27
	errors = [errors; spatio_nt(~isnan(spatio_nt(:,spatio_nt_medians_sort(ii))),spatio_nt_medians_sort(ii))];
	grp = [grp; (ii-1)*ones(sum(~isnan(spatio_nt(:,spatio_nt_medians_sort(ii)))),1)];
end
spatio_nt_median_markers = cell(27,1);
for ii=1:27
	spatio_nt_median_markers{ii} = [num2str(mod((spatio_nt_medians_sort(ii)-1),3)+1),',',num2str(mod(floor((spatio_nt_medians_sort(ii)-1)/3),3)+1),',',num2str(floor((spatio_nt_medians_sort(ii)-1)/3/3)+1)];
end
boxplot(errors,grp,'labels',spatio_nt_median_markers)
ylim([-0.1,1])

set( gca     , 'FontName'   , 'Helvetica' );
set([gca]    , 'FontSize'   , 16           );
set(findobj(gca,'Type','text'),'FontSize',16)
