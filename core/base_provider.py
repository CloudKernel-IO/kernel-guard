"""Clase base abstracta para todos los providers cloud"""


class CloudProvider:
    """
    Clase base para implementar providers de diferentes clouds.
    Cada provider debe implementar el método scan().
    """
    
    def scan(self, target: str):
        """
        Escanea recursos en el cloud provider.
        
        Args:
            target: Identificador del recurso a escanear (Resource Group, Región, Project ID)
        
        Returns:
            Lista de tuplas [nombre_recurso, tipo, hallazgo]
        
        Raises:
            NotImplementedError: Si el método no está implementado en la subclase
        """
        raise NotImplementedError("Subclasses must implement the scan() method")