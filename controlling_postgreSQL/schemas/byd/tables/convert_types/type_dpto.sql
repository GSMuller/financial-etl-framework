DROP TRIGGER IF EXISTS trigger_calcula_bonus_na_filha ON byd.byd_cadastro;

ALTER TABLE byd.byd_cadastro
    ALTER COLUMN trade TYPE TEXT;

-- Recrie o trigger aqui com a definição original
-- CREATE TRIGGER trigger_calcula_bonus_na_filha ...

CREATE TRIGGER trigger_calcula_bonus
BEFORE INSERT OR UPDATE ON byd.byd_cadastro
FOR EACH ROW
EXECUTE FUNCTION bonus_calculation();