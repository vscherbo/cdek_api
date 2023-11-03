DROP FUNCTION shp.cdek_sender(integer);

CREATE OR REPLACE FUNCTION shp.cdek_sender(shpid integer, OUT company character varying, OUT name character varying, OUT email character varying)
 RETURNS record
 LANGUAGE plpgsql
AS $function$
DECLARE
res_sender varchar;
begin
if shpid <= 0 then
    -- select company, "name", email from shp.stub_cdek_sender(shpid);
    select * into company, "name", email from shp.stub_cdek_sender(shpid);
else -- prod
    SELECT Счета.фирма INTO company
    FROM ship_bills INNER JOIN Счета ON ship_bills.bill = Счета."№ счета"
    WHERE ship_bills.shp_id=shpid;
    "name" := 'sender';
    email := 'buh@kipspb.ru';
end if; -- prod
end;
$function$
;

