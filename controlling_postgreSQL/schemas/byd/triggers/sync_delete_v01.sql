BEGIN
    IF OLD.idnfsexterno IS NOT NULL THEN
        DELETE FROM byd.byd_cadastro WHERE idnfsexterno = OLD.idnfsexterno;
        DELETE FROM byd.controladoria WHERE idnfsexterno = OLD.idnfsexterno;
    END IF;
    RETURN OLD;
END;