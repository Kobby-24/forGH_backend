from pwdlib import PasswordHash

class Hash: 
    ph = PasswordHash.recommended()
    @staticmethod
    def bcrypt(password: str) -> str:

        return Hash.ph.hash(password)

    @staticmethod
    def verify(hashed_password: str, plain_password: str) -> bool:
        return Hash.ph.verify(plain_password, hashed_password)