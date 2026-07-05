"""
WebSocket 路由 - 实时推送分析进度和结果
"""
import json
import asyncio
from typing import Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

router = APIRouter(tags=["websocket"])

# 连接管理
active_connections: Dict[int, WebSocket] = {}


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # evidence_id -> list of websockets
        self.connections: Dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, evidence_id: int):
        await websocket.accept()
        if evidence_id not in self.connections:
            self.connections[evidence_id] = []
        self.connections[evidence_id].append(websocket)

    def disconnect(self, websocket: WebSocket, evidence_id: int):
        if evidence_id in self.connections:
            self.connections[evidence_id].remove(websocket)
            if not self.connections[evidence_id]:
                del self.connections[evidence_id]

    async def broadcast(self, evidence_id: int, message: dict):
        if evidence_id in self.connections:
            msg = json.dumps(message, ensure_ascii=False, default=str)
            for ws in self.connections[evidence_id]:
                try:
                    await ws.send_text(msg)
                except RuntimeError:
                    pass

    async def broadcast_all(self, message: dict):
        msg = json.dumps(message, ensure_ascii=False, default=str)
        for evidence_id, connections in self.connections.items():
            for ws in connections:
                try:
                    await ws.send_text(msg)
                except RuntimeError:
                    pass


manager = ConnectionManager()


@router.websocket("/ws/{evidence_id}")
async def websocket_endpoint(websocket: WebSocket, evidence_id: int):
    """
    WebSocket 端点 - 为特定证据推送实时更新
    """
    await manager.connect(websocket, evidence_id)

    try:
        while True:
            # 接收客户端消息（可选，用于控制订阅）
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "subscribe":
                pass  # 已经订阅了
            elif msg.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))

    except WebSocketDisconnect:
        manager.disconnect(websocket, evidence_id)


@router.websocket("/ws/all")
async def websocket_all(websocket: WebSocket):
    """
    WebSocket 端点 - 监听所有证据的更新
    """
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))

    except WebSocketDisconnect:
        pass
