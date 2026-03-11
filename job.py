import uuid

class Job:
    def __init__(self, nk_path, writes, frame_range=None):
        self.id = str(uuid.uuid4())
        self.nk_path = nk_path
        self.writes = writes
        self.frame_range = frame_range
        self.status = "waiting"



    def to_dict(self):
        """ Converte o job para dicionário. Necessário para salvar em JSON """

        return {
            "id" : self.id,
            "nk_path" : self.nk_path,
            "writes" : self.writes,
            "frame_range" : self.frame_range,
            "status" : self.status
        }
    


    @classmethod
    def from_dict(cls, data):
        """RECRIA UM JOB A PARTIR DE UM DICIONARIO. Necessário para carregar do JSON"""
        job = cls(data["nk_path"], data["writes"], data["frame_range"])
        job.id = data["id"]
        job.status = data["status"]
        return job