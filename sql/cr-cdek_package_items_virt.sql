DROP FUNCTION shp.cdek_package_items_virt(shp_id integer, integer, integer);

CREATE OR REPLACE FUNCTION shp.cdek_package_items_virt(shp_id integer, box_number integer, total_boxes integer)
RETURNS TABLE (
    "name" varchar(255),
    ware_key varchar (20),
    cost numeric,
    weight integer,
    amount integer
)
LANGUAGE plpgsql
AS $function$
DECLARE
box_cost numeric;
box_weight integer;
begin
    -- вычислить box_cost для текущего box_number как долю 1/total_boxes от общей стоимости (руб)
    -- вычислить box_weight для текущего box_number как долю 1/total_boxes от общего веса (гр)
    box_cost := 789;
    box_weight := 123;
    return query 
    VALUES
    ('Приборы'::varchar, --name
        123456789::varchar, -- fake KC
        box_cost, -- cost of box_number
        box_weight, -- weight of box_number
        1 -- amount - fake, always 1
    );

end;
$function$
;
