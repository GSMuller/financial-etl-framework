BEGIN
    NEW.data_atualizacao = NOW();
    RETURN NEW;
END;
