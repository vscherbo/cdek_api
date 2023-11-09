-- DROP FUNCTION shp.cdek_package_items_virt(shp_id integer, integer, integer, numeric, numeric);
DROP FUNCTION shp.cdek_package_items_virt(shp_id integer, integer, integer, numeric, integer);

CREATE OR REPLACE FUNCTION shp.cdek_package_items_virt(shp_id integer, box_number integer, total_boxes integer,
total_sum numeric, box_weight integer)
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
part numeric;
begin
    -- вычислить box_cost для текущего box_number как долю 1/total_boxes от общей стоимости (руб)
    -- вычислить box_weight для текущего box_number как долю 1/total_boxes от общего веса (гр)
    --box_cost := 789;
    --box_weight := 123;
    part = 1::numeric/total_boxes;
    RAISE NOTICE 'box_number=%, part=%, total_boxes=%', box_number, part, total_boxes;
    if box_number = total_boxes then -- last boxes
        -- TODO получить вычитанием из общей суммы/веса всех предыдущих частей
        box_cost := round(part*total_sum, 2);
    else
        box_cost := round(part*total_sum, 2);
    end if;

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
