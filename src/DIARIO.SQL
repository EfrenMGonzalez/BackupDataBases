-- Declaración de las variables

DECLARE @PathBase nvarchar(500)
DECLARE @Path nvarchar(500)
DECLARE @File nvarchar(500)
DECLARE @Cmd nvarchar(500)
DECLARE @DBName nvarchar(100)
DECLARE @Desc nvarchar(500)

-- Establezco el path donde voy a guardar los backups

SET @PathBase = '\\10.0.0.17\BACKUP_TRESS$\DIARIO\'

-- Creo un subdirectorio con la fecha actual con el formato "yyyymmdd"
SET @Path = @PathBase + CONVERT(char(8), GetDate(), 112) + '\ '
SET @Cmd = 'MD "' + @Path + '"'
EXEC master..xp_cmdshell @Cmd

 
-- Busco el nombre de todas las bases de datos, excepto las de sistema
DECLARE db_cursor CURSOR FOR
SELECT Name
FROM master.dbo.sysdatabases
WHERE Category != 16 AND Name NOT IN ('master','model','msdb','tempdb')
ORDER BY Name
 
-- Creo un cursor para recorrer las bases
OPEN db_cursor
FETCH NEXT FROM db_cursor INTO @DBName
WHILE @@FETCH_STATUS = 0
BEGIN
    BEGIN TRY

        -- Hago el backup de cada base, agregándole descripción
        -- y estableciendo que debe utilizarse compresión
        SET @File = @Path + @DBName + '.bak'
        SET @Desc = 'Backup de la base ' + @DBName + ' (' + CONVERT(varchar(100), GetDate(), 0) + ')'
        BACKUP DATABASE @DBName TO DISK = @File WITH FORMAT, COMPRESSION, MEDIADESCRIPTION = @Desc
 
    END TRY
    BEGIN CATCH

    END CATCH;

    FETCH NEXT FROM db_cursor INTO @DBName

END

-- Elimino el cursor
CLOSE db_cursor
DEALLOCATE db_cursor