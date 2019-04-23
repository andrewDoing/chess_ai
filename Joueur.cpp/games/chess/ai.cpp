// AI
// This is where you build your AI

#include "ai.hpp"
#include <vector>
#include <sstream>

/// <summary>
/// std::string split implementation by using delimiter as a character.
/// </summary>
std::vector<std::string> string_split(std::string str_to_split, char delimeter)
{
    std::stringstream ss(str_to_split);
    std::string item;
    std::vector<std::string> split_strings;
    while (std::getline(ss, item, delimeter))
    {
        split_strings.push_back(item);
    }

    return split_strings;
}

/// <summary>
/// Pretty formats an FEN string to a human readable string.
///
/// For more information on FEN (Forsyth-Edwards Notation) strings see:
/// https://wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation
/// </summary>
std::string prettyFEN(std::string fen, std::string us)
{
    // split the FEN string up to help parse it
    auto split = string_split(fen, ' ');
    auto first = split[0]; // the first part is always the board locations

    auto sideToMove = split[1].at(0); // always the second part for side to move
    auto usOrThem = sideToMove == us.at(0) ? "us" : "them";

    auto fullmove = split[5]; // always the sixth part for the full move

    auto lines = string_split(first, '/');
    std::stringstream strings;
    strings << "Move: " << fullmove << "\n"
            << "Side to move: " << sideToMove << " (" << usOrThem << ")\n"
            << "   +-----------------+";

    int i = -1;
    for (auto line : lines)
    {
        i++;
        strings << "\n " << (8 - i) << " |";
        for (char &character : line)
        {
            int asInt = (int)character - 48; // test for char '1' -> int 1
            if (asInt > -1 && asInt < 9)
            {
                // blank tiles n times, so repeat the . that many times
                for (int j = 0; j < asInt; j++)
                {
                    strings << " .";
                }
            }
            else
            {
                // it was a regular character for a piece
                strings << ' ' << character;
            }
        }
        strings << " |";
    }
    strings << "\n   +-----------------+\n     a b c d e f g h\n";

    return strings.str();
}

namespace cpp_client
{

namespace chess
{

/// <summary>
/// This returns your AI's name to the game server.
/// Replace the string name.
/// </summary>
/// <returns>The name of your AI.</returns>
std::string AI::get_name() const
{
    // REPLACE WITH YOUR TEAM NAME!
    return "Chess C++ Player";
}

/// <summary>
/// This is automatically called when the game first starts, once the game objects are created
/// </summary>
void AI::start()
{
    // This is a good place to initialize any variables
}

/// <summary>
/// This is automatically called the game (or anything in it) updates
/// </summary>
void AI::game_updated()
{
    // If a function you call triggers an update this will be called before it returns.
}

/// <summary>
/// This is automatically called when the game ends.
/// </summary>
/// <param name="won">true if you won, false otherwise</param>
/// <param name="reason">An explanation for why you either won or lost</param>
void AI::ended(bool won, const std::string &reason)
{
    // You can do any cleanup of your AI here.  The program ends when this function returns.
}

/// <summary>
/// This is called every time it is this AI.player's turn to make a move.
/// </summary>
/// <returns>A string in Standard Algebriac Notation (SAN) for the move you want to make. If the move is invalid or not properly formatted you will lose the game.</returns>
std::string AI::make_move()
{
    /*******************************************************************************************************
     * IMPORTANT SERVER VARIABLES TO KNOW:
     *******************************************************************************************************
     * 
     * * Game.History
     *      - The list of moves that have occurred in the game so far in SAN.
     *
     * * Game.Fen
     *      - The FEN string representing the current board state. Updated every turn
     *      - For more info about FEN strings: https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation
     *
     * * Player
     *      - Your player object.
     *      - Important properties:
     *          * Player.Color
     *              - Your client's color ("white" or "black")
     *          * Player.Opponent
     *              - Your opponent's player object.
     *
     * NOTE THAT ALL OBJECT INFORMATION IS CONTAINED IN Joueur.cpp/games/chess/
     * HOWEVER, DO NOT CHANGE ANY OF THESE FILES EXCEPT FOR ai.cpp, ai.hpp, AND ANY OTHER FILES YOU MAY ADD YOURSELF
     * 
     *******************************************************************************************************
     * STANDARD ALGEBRAIC NOTATION
     *******************************************************************************************************
     * 
     * * When returning your move in Standard Algebraic Notation (SAN), the way I recommend is to first
     *   indicate the piece type if the piece is not a pawn, then the starting square's file and rank, then
     *   an x if there is a capture, then the ending square's file and rank.
     *   
     * * Pieces are indicated as R for Rook, N for Knight, B for Bishop, Q for Queen, and K for King. Pawns
     *   are not denoted by any letter.
     * 
     * * For castling in SAN, king-side castling is indicated by "O-O", while queen-side castling is
     *   indicated by "O-O-O".
     * 
     * * To promote a pawn when it reaches the other side of the board, add the type of piece to promote to
     *   at the end of the string.
     *   
     * * All SAN is case sensitive.
     * 
     * * Some examples:
     *      - Move a pawn from a2 to a4: a2a4
     *      - Capture a piece with a pawn from c6 to d5: c6xd5
     *      - Move a knight from b1 to c3: Nb1c3
     *      - Capture a piece with a queen from h3 to e6: Qh3xe6
     *      - King-side castle: O-O
     *      
     * * For more info about SAN: https://en.wikipedia.org/wiki/Algebraic_notation_(chess)
     * 
     *******************************************************************************************************/

    std::cout << prettyFEN(this->game->fen, this->player->color);

    // This will only work if we are black move the pawn at b2 to b3.
    // Otherwise we will lose.
    // Your job is to code SOMETHING to parse the FEN string in some way to determine a valid move, in SAN format.
    return "b3";
}

// You can add additional methods here for your AI to call

} // namespace chess

} // namespace cpp_client
