from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class DadosAnimalBase(BaseModel):
    raca: str
    peso_medio: float
    id: int

class DadosAnimalCreate(DadosAnimalBase):
    pass

class DadosAnimal(DadosAnimalBase):
    model_config = ConfigDict(from_attributes=True)


class AnimalBase(BaseModel):
    sexo: str
    id_dados_animal: int

class AnimalCreate(AnimalBase):
   id: int

class Animal(AnimalBase):
    model_config = ConfigDict(from_attributes=True)

class ControlePesagemBase(BaseModel):
    id_animal: int
    datahora_pesagem: datetime
    medicao_peso: float
    observacoes: Optional[str]

class ControlePesagemCreate(ControlePesagemBase):
    pass

class ControlePesagem(ControlePesagemBase):
    model_config = ConfigDict(from_attributes=True)