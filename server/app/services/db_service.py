from app.models import Session


class DBService:
    
    def create_session(
            self,
            api_key: str,
            device_id: str
        ) -> Session:
        """
        Create a route session in database

        Args:
            api_key (str): User API key
            device_id (str): User device ID

        Returns:
            Session: Created route session
        """
        # TODO: validate user with api_key
        session = Session(device_id)
        #TODO: save session in SESSION table

        return session
    
    def register_samples(
            self, 
            samples: list[dict],
            session_id: str,
            device_id: str
        ) -> None:
        """
        Save IMU sensor buffer in database

        Args:
            samples (list[dict]): IMU samples to save
            session_id (str): ID of the active session
            device_id (str): User device ID
        """
        #TODO: save buffer in ROUTE table with session_id as index
        pass