BEGIN
    -- Copia o valor BOOLEAN diretamente
    UPDATE byd.byd_cadastro f
    SET refaturado = NEW.refaturado 
    WHERE f.IDNFSEXTERNO = NEW.IDNFSEXTERNO;
    
    RETURN NEW;
END;
