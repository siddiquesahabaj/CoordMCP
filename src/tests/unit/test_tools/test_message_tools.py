"""
Unit tests for messaging tools.

Tests agent messaging functionality including sending, receiving, and broadcast messages.
Note: Tests mock the fastmcp dependencies due to environment constraints.
"""

import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.unit
@pytest.mark.tools

class TestSendMessage:
    """Test message sending."""
    
    @pytest.mark.asyncio
    async def test_send_message_success(self, memory_store, context_manager, sample_project_id):
        """Test successful message sending."""
        from coordmcp.tools import message_tools
        
        # Create sender and recipient
        sender_id = context_manager.register_agent("Sender", "opencode")
        recipient_id = context_manager.register_agent("Recipient", "cursor")
        
        with patch.object(message_tools, 'get_memory_store', return_value=memory_store), \
             patch.object(message_tools, 'get_context_manager', return_value=context_manager):
            
            result = await message_tools.send_message(
                from_agent_id=sender_id,
                to_agent_id=recipient_id,
                project_id=sample_project_id,
                content="Hello from sender!"
            )
            
            assert result["success"] is True
            assert "message_id" in result
    
    @pytest.mark.asyncio
    async def test_send_message_broadcast(self, memory_store, context_manager, sample_project_id):
        """Test broadcast message to all agents."""
        from coordmcp.tools import message_tools
        
        sender_id = context_manager.register_agent("Broadcaster", "opencode")
        
        with patch.object(message_tools, 'get_memory_store', return_value=memory_store), \
             patch.object(message_tools, 'get_context_manager', return_value=context_manager):
            
            result = await message_tools.send_message(
                from_agent_id=sender_id,
                to_agent_id="broadcast",
                project_id=sample_project_id,
                content="Broadcast message!",
                message_type="alert"
            )
            
            assert result["success"] is True
            assert "all agents" in result["message"].lower()
    
    @pytest.mark.asyncio
    async def test_send_message_invalid_recipient(self, memory_store, context_manager, sample_project_id):
        """Test that sending to nonexistent recipient fails."""
        from coordmcp.tools import message_tools
        
        sender_id = context_manager.register_agent("Sender", "opencode")
        
        with patch.object(message_tools, 'get_memory_store', return_value=memory_store), \
             patch.object(message_tools, 'get_context_manager', return_value=context_manager):
            
            result = await message_tools.send_message(
                from_agent_id=sender_id,
                to_agent_id="nonexistent-agent",
                project_id=sample_project_id,
                content="Hello"
            )
            
            assert result["success"] is False
            assert "not found" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_send_message_invalid_type_defaults(self, memory_store, context_manager, sample_project_id):
        """Test that invalid message type defaults to update."""
        from coordmcp.tools import message_tools
        
        sender_id = context_manager.register_agent("Sender", "opencode")
        recipient_id = context_manager.register_agent("Recipient", "cursor")
        
        with patch.object(message_tools, 'get_memory_store', return_value=memory_store), \
             patch.object(message_tools, 'get_context_manager', return_value=context_manager):
            
            result = await message_tools.send_message(
                from_agent_id=sender_id,
                to_agent_id=recipient_id,
                project_id=sample_project_id,
                content="Test",
                message_type="invalid_type"
            )
            
            # Should succeed with default type
            assert result["success"] is True


@pytest.mark.unit
@pytest.mark.tools

class TestGetMessages:
    """Test message retrieval."""
    
    @pytest.mark.asyncio
    async def test_get_messages_for_agent(self, memory_store, context_manager, sample_project_id):
        """Test getting messages for an agent."""
        from coordmcp.tools import message_tools
        from tests.utils.factories import AgentMessageFactory
        
        # Create agents
        sender_id = context_manager.register_agent("Sender", "opencode")
        recipient_id = context_manager.register_agent("Recipient", "cursor")
        
        # Create messages
        for i in range(3):
            msg = AgentMessageFactory.create(
                from_agent_id=sender_id,
                to_agent_id=recipient_id,
                project_id=sample_project_id
            )
            memory_store.send_message(msg)
        
        with patch.object(message_tools, 'get_memory_store', return_value=memory_store), \
             patch.object(message_tools, 'resolve_project_id', return_value=(True, sample_project_id, "OK")):
            
            result = await message_tools.get_messages(
                agent_id=recipient_id,
                project_id=sample_project_id
            )
            
            assert result["success"] is True
            assert result["count"] == 3
    
    @pytest.mark.asyncio
    async def test_get_unread_messages_only(self, memory_store, context_manager, sample_project_id):
        """Test filtering to unread messages only."""
        from coordmcp.tools import message_tools
        from tests.utils.factories import AgentMessageFactory
        
        sender_id = context_manager.register_agent("Sender", "opencode")
        recipient_id = context_manager.register_agent("Recipient", "cursor")
        
        # Create messages
        msg1 = AgentMessageFactory.create(
            from_agent_id=sender_id,
            to_agent_id=recipient_id,
            project_id=sample_project_id
        )
        memory_store.send_message(msg1)
        
        msg2 = AgentMessageFactory.create(
            from_agent_id=sender_id,
            to_agent_id=recipient_id,
            project_id=sample_project_id,
            read=True
        )
        memory_store.send_message(msg2)
        
        with patch.object(message_tools, 'get_memory_store', return_value=memory_store), \
             patch.object(message_tools, 'resolve_project_id', return_value=(True, sample_project_id, "OK")):
            
            result = await message_tools.get_messages(
                agent_id=recipient_id,
                project_id=sample_project_id,
                unread_only=True
            )
            
            assert result["success"] is True
            assert result["count"] == 1


@pytest.mark.unit
@pytest.mark.tools

class TestMarkMessageRead:
    """Test marking messages as read."""
    
    @pytest.mark.asyncio
    async def test_mark_message_read_success(self, memory_store, context_manager, sample_project_id):
        """Test successfully marking a message as read."""
        from coordmcp.tools import message_tools
        from tests.utils.factories import AgentMessageFactory
        
        sender_id = context_manager.register_agent("Sender", "opencode")
        recipient_id = context_manager.register_agent("Recipient", "cursor")
        
        msg = AgentMessageFactory.create(
            from_agent_id=sender_id,
            to_agent_id=recipient_id,
            project_id=sample_project_id
        )
        msg_id = memory_store.send_message(msg)
        
        with patch.object(message_tools, 'get_memory_store', return_value=memory_store), \
             patch.object(message_tools, 'resolve_project_id', return_value=(True, sample_project_id, "OK")):
            
            result = await message_tools.mark_message_read(
                agent_id=recipient_id,
                message_id=msg_id,
                project_id=sample_project_id
            )
            
            assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_mark_message_read_wrong_recipient(self, memory_store, sample_project_id):
        """Test that marking read fails for wrong recipient."""
        from coordmcp.tools import message_tools
        from tests.utils.factories import AgentMessageFactory
        
        msg = AgentMessageFactory.create(
            from_agent_id="sender",
            to_agent_id="intended-recipient",
            project_id=sample_project_id
        )
        msg_id = memory_store.send_message(msg)
        
        with patch.object(message_tools, 'get_memory_store', return_value=memory_store), \
             patch.object(message_tools, 'resolve_project_id', return_value=(True, sample_project_id, "OK")):
            
            result = await message_tools.mark_message_read(
                agent_id="wrong-recipient",
                message_id=msg_id,
                project_id=sample_project_id
            )
            
            assert result["success"] is False


@pytest.mark.unit
@pytest.mark.tools

class TestBroadcastMessage:
    """Test broadcast messaging."""
    
    @pytest.mark.asyncio
    async def test_broadcast_message(self, memory_store, context_manager, sample_project_id):
        """Test broadcasting a message to all agents."""
        from coordmcp.tools import message_tools
        
        sender_id = context_manager.register_agent("Broadcaster", "opencode")
        
        with patch.object(message_tools, 'get_memory_store', return_value=memory_store), \
             patch.object(message_tools, 'get_context_manager', return_value=context_manager):
            
            result = await message_tools.broadcast_message(
                from_agent_id=sender_id,
                project_id=sample_project_id,
                content="Attention all agents!",
                message_type="alert"
            )
            
            assert result["success"] is True


@pytest.mark.unit
@pytest.mark.tools

class TestGetSentMessages:
    """Test getting sent messages."""
    
    @pytest.mark.asyncio
    async def test_get_sent_messages(self, memory_store, context_manager, sample_project_id):
        """Test getting messages sent by an agent."""
        from coordmcp.tools import message_tools
        from tests.utils.factories import AgentMessageFactory
        
        sender_id = context_manager.register_agent("Sender", "opencode")
        recipient_id = context_manager.register_agent("Recipient", "cursor")
        
        # Send some messages
        for i in range(2):
            msg = AgentMessageFactory.create(
                from_agent_id=sender_id,
                to_agent_id=recipient_id,
                project_id=sample_project_id
            )
            memory_store.send_message(msg)
        
        with patch.object(message_tools, 'get_memory_store', return_value=memory_store), \
             patch.object(message_tools, 'resolve_project_id', return_value=(True, sample_project_id, "OK")):
            
            result = await message_tools.get_sent_messages(
                agent_id=sender_id,
                project_id=sample_project_id
            )
            
            assert result["success"] is True
            assert result["count"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
