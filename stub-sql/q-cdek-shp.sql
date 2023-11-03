select distinct on (sb.shp_id) sb.shp_id 
,sb.bill , b."ДокТК" , b.dt_create 
--select sb.bill , sb.shp_id
--select count (sb.shp_id), sb.shp_id
from shp.delivery d 
join shp.ship_bills sb on sb.dlvrid = d.dlvr_id 
join shp.shipments s on s.shp_id = sb.shp_id 
join "Счета" b on b."№ счета" = sb.bill 
where d.carr_id = 44
and s.shipdate  > '2023-09-15' and s.shipdate  < '2023-11-01'
and фирма = 'ЭТК'
and b."ДокТК" is not null
