-- shp.cdek_preorder_params определение

-- Drop table

-- DROP TABLE shp.cdek_preorder_params;

CREATE TABLE shp.cdek_preorder_params (
    id serial4 NOT NULL,
    credate timestamp NULL DEFAULT now(),
    cdek_number varchar NULL,
    cdek_uuid uuid NULL,
    our_number varchar NULL,
    sts_code int4 NOT NULL DEFAULT 0, -- 0-создан, 10-принят, 20-верифицирован, 90-не принят, 91-некорректный
    ret_code int4 NULL,
    ret_msg varchar NULL,
    shp_id int4 NULL,
    payload json NULL,
    barcode_uuid uuid NULL,
    our_firm varchar NULL,
    dl_status int4 NULL,
    CONSTRAINT cdek_preorder_params_pk PRIMARY KEY (id),
    CONSTRAINT cdek_preorder_params_un UNIQUE (shp_id)
);

-- Column comments

COMMENT ON COLUMN shp.cdek_preorder_params.sts_code IS '0-создан, 10-принят, 20-верифицирован, 90-не принят, 91-некорректный';

-- Table Triggers

CREATE TRIGGER tr_bcu AFTER
UPDATE
    OF barcode_uuid ON
    shp.cdek_preorder_params FOR EACH ROW
    WHEN ((new.barcode_uuid IS NOT NULL)) EXECUTE PROCEDURE fntr_bcu();
CREATE TRIGGER tr_stscode AFTER
UPDATE
    OF sts_code ON
    shp.cdek_preorder_params FOR EACH ROW
    WHEN (((new.sts_code = 20)
        AND (old.sts_code = 10))) EXECUTE PROCEDURE fntr_stscode();
