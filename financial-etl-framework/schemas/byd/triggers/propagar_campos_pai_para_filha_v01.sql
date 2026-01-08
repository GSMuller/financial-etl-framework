BEGIN
    UPDATE byd.byd_cadastro f
    SET 
        tipo_transacao = NEW.tipo_transacao,
        status_nf = NEW.status_nf
    WHERE f.idnfsexterno = NEW.idnfsexterno;
    
    RETURN NEW;
END;
