# Envoi de secours vers Infomaniak, utilisé seulement si lftp n'a pas pu être installé.
# SFTP d'abord (paramiko), puis FTP chiffré. N'efface rien sur le serveur.
# Les images/vidéos à nom unique (ev-, th-, lsf-) ne sont renvoyées que si la taille diffère.
import os, sys, fnmatch, ftplib, socket

HOTE, USER, MDP = os.environ["HOTE"], os.environ["UTILISATEUR"], os.environ["LFTP_PASSWORD"]
EXCLU = [".*", "apercu*", "comparaison*", "LISEZMOI*", "A-SUPPRIMER*", "a-importer*.json", "README.md"]
UNIQUES = ["ev-*.jpg", "th-*.jpg", "lsf-*.mp4", "lsf-*.jpg"]

def fichiers():
    for racine, dossiers, noms in os.walk("."):
        dossiers[:] = [d for d in dossiers if not any(fnmatch.fnmatch(d, e) for e in EXCLU)]
        for n in noms:
            if any(fnmatch.fnmatch(n, e) for e in EXCLU):
                continue
            yield os.path.relpath(os.path.join(racine, n), ".")

def unique(chemin):
    return any(fnmatch.fnmatch(os.path.basename(chemin), u) for u in UNIQUES)

def par_sftp():
    import paramiko
    t = paramiko.Transport((HOTE, 22)); t.connect(username=USER, password=MDP)
    s = paramiko.SFTPClient.from_transport(t)
    for f in fichiers():
        d = os.path.dirname(f)
        if d:
            try: s.mkdir(d)
            except IOError: pass
        if unique(f):
            try:
                if s.stat(f).st_size == os.path.getsize(f): continue
            except IOError: pass
        s.put(f, f); print("SFTP", f)
    s.close(); t.close()

def par_ftps():
    c = ftplib.FTP_TLS(HOTE, timeout=60); c.login(USER, MDP); c.prot_p()
    for f in fichiers():
        d = os.path.dirname(f)
        if d:
            try: c.mkd(d)
            except ftplib.error_perm: pass
        if unique(f):
            try:
                c.voidcmd("TYPE I")
                if c.size(f) == os.path.getsize(f): continue
            except ftplib.error_perm: pass
        with open(f, "rb") as h: c.storbinary("STOR " + f, h)
        print("FTPS", f)
    c.quit()

try:
    par_sftp(); print("Publication réussie en SFTP (secours)")
except Exception as e:
    print("SFTP refusé :", e, "— essai en FTP chiffré")
    par_ftps(); print("Publication réussie en FTP chiffré (secours)")
