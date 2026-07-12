from flask_restful import Resource
from src.services.uart_service import UartService

class ListUart(Resource):
    def get(self):
        service = UartService()
        uart_port_list = service.list_uart_ports()

        if not uart_port_list != None:
            return {"error": "Some error occurred"}, 400
        return {'uart_ports': uart_port_list}, 200
