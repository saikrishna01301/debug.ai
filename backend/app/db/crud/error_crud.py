from app.db.models.error import ParsedError, Analysis
from sqlalchemy.ext.asyncio import AsyncSession


async def create_parsed_error(session: AsyncSession, parsed_error_data: dict) -> ParsedError:
    """Create a new parsed error in the database"""
    # Map the parsed_error dictionary to the ParsedError model fields
    error_data = {
        "raw_error_log": parsed_error_data.get("raw_error_log", ""),
        "error_type": parsed_error_data.get("error_type", ""),
        "error_message": parsed_error_data.get("error_message", ""),
        "language": parsed_error_data.get("language"),
        "framework": parsed_error_data.get("framework"),
        "file_name": parsed_error_data.get("file_path"),  # Note: using file_path from parser
        "line_number": parsed_error_data.get("line_number"),
        "function_name": parsed_error_data.get("function_name"),
        "stack_trace": parsed_error_data.get("stack_trace"),
        "confidence_score": parsed_error_data.get("confidence_score"),
    }

    parsed_error = ParsedError(**error_data)
    session.add(parsed_error)
    await session.commit()
    await session.refresh(parsed_error)
    return parsed_error


async def create_analysis(session: AsyncSession, analysis_data: dict) -> Analysis:
    """Create a new analysis in the database"""
    analysis = Analysis(**analysis_data)
    session.add(analysis)
    await session.commit()
    await session.refresh(analysis)
    return analysis
