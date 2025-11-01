from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from services.qr_callback import QRCallbackCache

router = APIRouter(prefix="/qr")

@router.websocket("/{payment_id}/callback")
async def test_qr_callback_websocket(
    websocket: WebSocket,
    payment_id: str
):
    await websocket.accept()
    
    try:
        await QRCallbackCache.set_waiting_status(payment_id)
        
        async def check_payment_status():
            for i in range(30):
                try:
                    status = await QRCallbackCache.get_status(payment_id)
                    
                    await websocket.send_json({
                        "second": i + 1,
                        "status": status or "None"
                    })
                    
                    if status is None:
                        await websocket.send_json({
                            "status": "error",
                            "message": "Payment ID not found"
                        })
                        return
                    
                    if status == QRCallbackCache.COMPLETED_STATUS:
                        await websocket.send_json({
                            "status": "completed",
                            "payment_id": payment_id,
                            "message": "Payment completed successfully"
                        })
                        return
                    
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    await websocket.send_json({
                        "status": "error",
                        "message": str(e)
                    })
                    return
            
            await websocket.send_json({
                "status": "timeout",
                "message": "Connection timeout after 30 seconds"
            })
        
        await check_payment_status()
        
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({
                "status": "error",
                "message": str(e)
            })
        except:
            pass
    finally:
        await QRCallbackCache.delete_status(payment_id)
        try:
            await websocket.close()
        except:
            pass


@router.post("/{payment_id}/complete")
async def test_complete_payment(payment_id: str):
    try:
        await QRCallbackCache.set_completed_status(payment_id)
        
        return {
            "status": "success",
            "payment_id": payment_id,
            "message": "Payment status updated to completed"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@router.get("/{payment_id}/status")
async def test_get_payment_status(payment_id: str):

    try:
        status = await QRCallbackCache.get_status(payment_id)
        
        return {
            "payment_id": payment_id,
            "status": status or "not_found",
            "message": f"Current status: {status}" if status else "Payment ID not found in cache"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@router.delete("/{payment_id}")
async def test_delete_payment_status(payment_id: str):

    try:
        await QRCallbackCache.delete_status(payment_id)
        
        return {
            "status": "success",
            "payment_id": payment_id,
            "message": "Payment status deleted"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }