using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using TMPro;
using Unity.Mathematics;
using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Sensors;
using System.Runtime.CompilerServices;
using UnityEngine.UIElements;
using JetBrains.Annotations;

public enum SlotStatuses
{
    Unfilled, Yellow, Red
}

public enum GameMode
{
    PvP, PvR, PvAI, RvAI, AIvAI
}

public class InstanceManager : MonoBehaviour
{
    public Dictionary<string, Color> colourData = new Dictionary<string, Color>();
    [Tooltip("(Columns, Rows)")]
    public List<byte> board_dims = new List<byte>(new byte[2]);
    public List<GameObject> slots;
    public GameMode gameMode;
    public List<float> col_positions;

    public TextMeshPro yellow_win_ratio_text;
    public TextMeshPro red_win_ratio_text;
    public TextMeshPro tie_ratio_text;
    public int total_games;

    int[,] board_matrix;
    private KeyCode[] keyCode_nums;
    public bool turn_played;
    GameObject pointer;
    Bounds board_bounds;
    public SlotStatuses current_turn;
    public bool gameFinished;
    public Dictionary<SlotStatuses, ulong> scores;
    public SlotStatuses ai_colour;
    public int debug_seed;
    public SlotStatuses latest_winner;

    public AgentManager yellowAgent;
    public AgentManager redAgent;
    public GameObject randomAgent;
    public GameObject playerAgent;

    public TextMeshPro cumReward;

    static System.Random random;

    void InitialiseTurn()
    {
        current_turn = ToggleTurn(ai_colour);
    }

    public AgentManager getAgentFromStatus(SlotStatuses status)
    {
        return (status == SlotStatuses.Yellow) ? yellowAgent : (status == SlotStatuses.Red) ? redAgent : null;
    }

    SlotStatuses ToggleTurn(SlotStatuses status)
    {
        if (status == SlotStatuses.Yellow)
        {
            return SlotStatuses.Red;
        }
        else if (status == SlotStatuses.Red)
        {
            return SlotStatuses.Yellow;
        }
        else
        {
            Debug.LogWarning("Warning: `SlotStatuses.Unfilled` cannot be toggled.");
            return status;
        }
    }

    SlotStatuses randomiseTurn()
    {
        int r = random.Next(0, 1);
        if (r == 0)
        {
            return SlotStatuses.Yellow;
        }
        else
        {
            return SlotStatuses.Red;
        }
    }

    public void SwitchAITurn(bool toggle = false)
    {

        if (toggle)
        {
            current_turn = ToggleTurn(current_turn);
        }
        if (current_turn == SlotStatuses.Yellow)
        {

            yellowAgent.RequestDecision();
        }
        else if (current_turn == SlotStatuses.Red)
        {
            redAgent.RequestDecision();
        }
    }

    public void DisplayMatrix(int[,] matrix)
    {

        string text = "[[";
        for (int i = 0; i < matrix.Length; i++)
        {
            int row = i % matrix.GetLength(0);
            int col = i % matrix.GetLength(1);


            if ((col + 1) % matrix.GetLength(1) == 0)
            {
                text += $"{matrix[row, col]}";
                if (i + 1 == matrix.Length)
                {
                    text += $"]]"; ;
                }
                else
                {
                    text += "],\n[";
                }
            }
            else
            {
                text += $"{matrix[row, col]}, ";
            }
        }
        Debug.Log(text);

    }

    public void DebugList(List<int> list)
    {
        string str = "{";
        for (int i = 0; i < list.Count; i++)
        {
            str += list[i].ToString();
            if (i + 1 < list.Count)
            {
                str += ", ";
            }
        }
        str += "}";
        Debug.Log(str);
    }

    public void DebugList(IEnumerable list)
    {
        string str = "[";

        foreach (var e in list)
        {
            str += e.ToString() + " ";
        }

        str += "]";
        Debug.Log(str);
    }


    public int[,] GetMatrix(List<GameObject> slots)
    {
        int[,] matrix = new int[board_dims[1], board_dims[0]];

        foreach (GameObject slot in slots)
        {
            List<int> slot_pos = slot.GetComponent<SlotData>().pos;
            matrix[slot_pos[0], slot_pos[1]] = (int)slot.GetComponent<SlotData>().slotStatus;
        }
        return matrix;
    }

    public List<int> LGetMatrix()
    {
        List<int> matrix = new List<int>();
        foreach (GameObject slot in slots)
        {
            matrix.Add((int)slot.GetComponent<SlotData>().slotStatus);
        }
        return matrix;
    }

    public List<float> LGetNormalisedMatrix()
    {

        List<int> matrix = LGetMatrix();
        int max_val = matrix.Max();
        int min_val = matrix.Min();

        List<float> normalised_matrix = new List<float>();
        foreach (int s in matrix)
        {
            normalised_matrix.Add(NormaliseValue(s, min_val, max_val)) ;
        }

        return normalised_matrix;
    }

    private static float NormaliseValue(int val, int min_val, int max_val)
    {
        if(min_val == max_val) { return 0; }
        return (2 * (val - min_val) / (max_val - min_val)) - 1;
    }

    public long Base3ToDecimal(string num_str)
    {
        long new_num = 0;

        char[] char_ar = num_str.ToCharArray();
        Array.Reverse(char_ar);

        for (int i = 0; i < char_ar.Length; i++)
        {
            new_num += char_ar[i] * (int)math.pow(3,i);
        }
        return new_num;
    }

    public long GetBoardHash()
    {
        float[] statuses = GetStatuses(slots);

        string num_str = "";

        foreach (float _status in statuses)
        {
            num_str += _status;
        }

        return Base3ToDecimal(num_str);

    }

    public float NormaliseBoardHash(long board_hash)
    {
        long max = (long)math.pow(3, board_dims[0] * board_dims[1])-1;
        double val = (double)board_hash / (double)max;
        return (float)((val*2)-1);
    }

    private void UpdateBlockReward(SlotStatuses blockedStatus)
    {
        if (gameMode == GameMode.AIvAI)
        {
            getAgentFromStatus(ToggleTurn(blockedStatus)).AddReward(AgentConstants.blockReward);
            getAgentFromStatus(blockedStatus).AddReward(-(AgentConstants.blockReward));
        }
        if ((gameMode == GameMode.RvAI || gameMode == GameMode.PvAI) && ai_colour == ToggleTurn(blockedStatus))
        {
            getAgentFromStatus(ToggleTurn(blockedStatus)).AddReward(AgentConstants.blockReward);
            getAgentFromStatus(blockedStatus).AddReward(-(AgentConstants.blockReward));
        }
    }

    public float[] GetStatuses(List<GameObject> slots)
    {
        float[] statuses = new float[board_dims[0] * board_dims[1]];
        foreach (GameObject slot in slots)
        {
            statuses[slot.GetComponent<SlotData>().slotID] = (int)slot.GetComponent<SlotData>().slotStatus;
        }

        return statuses;
    }

    public MoveData CheckHorizontalWin(SlotStatuses status)
    {
        List<int> slot_data_temp = new List<int>();
        List<int> max_vals = new List<int>();
        byte n_in_row = 0;

        foreach (GameObject slot in slots)
        {
            if (slot.GetComponent<SlotData>().slotStatus == status)
            {
                slot_data_temp.Add(slot.GetComponent<SlotData>().slotID);
            }
        }

        foreach (int slotID in slot_data_temp)
        {
            if (slot_data_temp.Contains(slotID + 1))
            {
                if (slot_data_temp.Contains(slotID + 2))
                {
                    if (slot_data_temp.Contains(slotID + 3))
                    {
                        max_vals.Add(4);
                    }
                    else
                    {
                        max_vals.Add(3);
                        if (gameMode == GameMode.AIvAI)
                        {
                            if ((slotID + board_dims[0] + 3 < board_dims[0]) && slots[slotID + board_dims[0] + 3].GetComponent<SlotData>().slotStatus == ToggleTurn(status))
                            {
                                getAgentFromStatus(ToggleTurn(status)).AddReward(AgentConstants.blockReward);
                            }
                        }
                    }
                }
                else
                {
                    max_vals.Add(2);
                }
            }
            else
            {
                max_vals.Add(1);
            }
        }

        if (max_vals.Count > 0)
        {
            n_in_row = (byte)max_vals.Max();
        }
        else
        {
            n_in_row = 0;
        }


        if (n_in_row >= 4)
        {
            return new MoveData(status,true);
        }

        return new MoveData(status, false);
    }

    public MoveData CheckVerticalWin(SlotStatuses status)
    {

        List<int> slot_data_temp = new List<int>();
        List<int> max_vals = new List<int>();
        byte n_in_row = 0;

        foreach (GameObject slot in slots)
        {
            if (slot.GetComponent<SlotData>().slotStatus == status)
            {
                slot_data_temp.Add(slot.GetComponent<SlotData>().slotID);
            }
        }

        foreach (int slotID in slot_data_temp)
        {
            if (slot_data_temp.Contains(slotID + board_dims[0]))
            {
                if (slot_data_temp.Contains(slotID + board_dims[0] * 2))
                {
                    if (slot_data_temp.Contains(slotID + board_dims[0] * 3))
                    {
                        max_vals.Add(4);
                    }
                    else
                    {
                        
                        if(gameMode == GameMode.AIvAI || gameMode == GameMode.RvAI || gameMode == GameMode.PvAI)
                        {
                            if ((slotID + board_dims[0] * 3 < slots.Count) && slots[slotID + board_dims[0] * 3].GetComponent<SlotData>().slotStatus == ToggleTurn(status))
                            {
                                UpdateBlockReward(status);

                            }
                        }
                        max_vals.Add(3);
                    }
                }
                else
                {
                    max_vals.Add(2);
                }
            }
            else
            {
                max_vals.Add(1);
            }
        }

        //DebugList(max_vals);

        if (max_vals.Count > 0)
        {
            n_in_row = (byte)max_vals.Max();
        }
        else
        {
            n_in_row = 0;
        }

        if (n_in_row >= 4)
        {
            return new MoveData(status, true);
        }
        return new MoveData(status, false);
    }


    public MoveData CheckUpRightWin(SlotStatuses status, bool use_debug = false)
    {
        //UpRight = Increase horizontal, increase vertical

        List<int> slot_data_temp = new List<int>();
        List<byte> max_vals = new List<byte>();

        byte n_in_row = 0;
        for (int i = 0; i < slots.Count; i++)
        {
            if (slots[i].GetComponent<SlotData>().slotStatus == status)
            {
                slot_data_temp.Add(slots[i].GetComponent<SlotData>().slotID);
            }
        }

        for (int i = 0; i < slot_data_temp.Count; i++)
        {
            n_in_row = 1;
            for (int c = 1; c < 4; c++)
            {
                if (slot_data_temp.Contains(slot_data_temp[i] + (board_dims[0] + 1) * c))
                {
                    n_in_row++;
                    if (c == 3)
                    {
                        max_vals.Add(n_in_row);
                    }
                }
                else
                {
                    max_vals.Add(n_in_row);
                    
                    if(n_in_row == 3)
                    {
                        if(gameMode == GameMode.AIvAI || gameMode == GameMode.PvAI || gameMode == GameMode.RvAI)
                        {
                            if ((slot_data_temp[i] + (board_dims[0] + 1) * 3 < slots.Count) && slots[slot_data_temp[i] + (board_dims[0] + 1) * 3].GetComponent<SlotData>().slotStatus == ToggleTurn(status))
                            {
                                UpdateBlockReward(status);
                            }
                        }
                    }
                }
            }
        }
        if (max_vals.Count > 0)
        {
            n_in_row = (byte)max_vals.Max();
        }
        else
        {
            n_in_row = 0;
        }

        if (n_in_row >= 4)
        {
            return new MoveData(status, true);
        }
        return new MoveData(status, false);
    }

    public MoveData CheckDownRightWin(SlotStatuses status, bool use_debug = false)
    {
        //UpRight = Increase horizontal, increase vertical

        List<int> slot_data_temp = new List<int>();
        List<byte> max_vals = new List<byte>();

        byte n_in_row = 0;
        for (int i = 0; i < slots.Count; i++)
        {
            if (slots[i].GetComponent<SlotData>().slotStatus == status)
            {
                slot_data_temp.Add(slots[i].GetComponent<SlotData>().slotID);
            }
        }

        for (int i = 0; i < slot_data_temp.Count; i++)
        {
            n_in_row = 1;
            for (int c = 1; c < 4; c++)
            {

                if (slot_data_temp.Contains(slot_data_temp[i] - ((board_dims[0] - 1) * c)))
                {
                    n_in_row++;
                    if (c == 3)
                    {
                        max_vals.Add(n_in_row);
                    }
                }
                else
                {
                    max_vals.Add(n_in_row);
                    
                    if (n_in_row == 3)
                    {
                        if(gameMode == GameMode.AIvAI || gameMode == GameMode.RvAI || gameMode == GameMode.PvAI)
                        {
                            if ((slot_data_temp[i] - (board_dims[0] - 1) * 3 < slots.Count) && (slot_data_temp[i] - (board_dims[0] - 1) * 3 >= 0))
                            {
                                if (slots[slot_data_temp[i] - (board_dims[0] - 1) * 3].GetComponent<SlotData>().slotStatus == ToggleTurn(status))
                                {
                                    UpdateBlockReward(status);
                                }
                            }
                        }
                    }
                }
            }
        }
        if (max_vals.Count() > 0)
        {
            n_in_row = (byte)max_vals.Max(v => v);
        }
        else
        {
            n_in_row = 0;
        }

        if (n_in_row >= 4)
        {
            return new MoveData(status, true);
        }
        return new MoveData(status, false);
    }


    public bool CheckWin(SlotStatuses status)
    {

        MoveData horizontal_data = CheckHorizontalWin(status);
        MoveData vertical_data = CheckVerticalWin(status);
        MoveData upRight_data = CheckUpRightWin(status, false);
        MoveData downRight_data = CheckDownRightWin(status, false);

        if (horizontal_data.win || vertical_data.win || upRight_data.win || downRight_data.win)
        {

            if (gameMode == GameMode.PvP)
            {
                transform.parent.GetComponentInChildren<WinTextManager>(true).SetWinText(status, this);
            }
            if (gameMode == GameMode.PvP || gameMode == GameMode.PvAI)
            {
                transform.parent.Find("restart_text").gameObject.SetActive(true);
            }

            scores[status]++;
            transform.parent.Find("score_text_yellow").GetComponent<TextMeshPro>().text = scores[SlotStatuses.Yellow].ToString();
            transform.parent.Find("score_text_red").GetComponent<TextMeshPro>().text = scores[SlotStatuses.Red].ToString();
            //Debug.Log("Win!");
            //Time.timeScale = 0;
            total_games++;
            latest_winner = status;
            decimal yellow_win_ratio = total_games > 0 ? (decimal)scores[SlotStatuses.Yellow] / (decimal)total_games : 0;
            yellow_win_ratio = Math.Round(yellow_win_ratio, 4);
            decimal red_win_ratio = total_games > 0 ? (decimal)scores[SlotStatuses.Red] / (decimal)total_games : 0;
            red_win_ratio = Math.Round(red_win_ratio, 4);
            decimal tie_ratio = total_games > 0 ? 1 - yellow_win_ratio - red_win_ratio : 0;

            yellow_win_ratio_text.text = ((float)(yellow_win_ratio * 100)).ToString() + "%";
            red_win_ratio_text.text = ((float)(red_win_ratio * 100)).ToString() + "%";
            tie_ratio_text.text = ((float)(tie_ratio * 100)).ToString() + "%";
            gameFinished = true;
            return true;
        }
        return false;
    }

    bool IsBoardFull()
    {
        List<SlotStatuses> status_list = new List<SlotStatuses>();
        foreach (GameObject s in slots)
        {
            status_list.Add(s.GetComponent<SlotData>().slotStatus);
        }
        byte num_unfilled = (byte)(status_list.Where(status => status.Equals(SlotStatuses.Unfilled)).ToList<SlotStatuses>().Count);
        if (num_unfilled > 0)
        {
            return false;
        }
        else
        {
            return true;
        }

    }
    List<int> GetAvailableColumns()
    {
        List<int> available_cols = new List<int>();
        GameObject[,] slotArray2D = Get2DSlotArray();
        for(int i = 0; i < slotArray2D.GetLength(0); i++)
        {
            List<GameObject> col = new List<GameObject>(SelectColumn(slotArray2D, i));
            if (!IsColumnFull(col))
            {
                available_cols.Add(i);
            }
        }
        return available_cols;
    }

    public GameObject[] SelectColumn(GameObject[,] array, int colIndex)
    {
        GameObject[] column = new GameObject[array.GetLength(1)];
        for (int i = 0; i < array.GetLength(1); i++)
        {
            column[i] = array[colIndex, i];
      }
        return column;
    }

    public GameObject[,] Get2DSlotArray()
    {
        GameObject[,] slot_array = new GameObject[board_dims[0], board_dims[1]];

        foreach (GameObject slot in slots)
        {
            SlotData slotData = slot.GetComponent<SlotData>();
            int col = slotData.pos[0];
            int row = slotData.pos[1];
            slot_array[col,row] = slot;
        }
        return slot_array;
    }
    
    bool IsColumnFull(List<GameObject> column)
    {
        List<SlotStatuses> status_list = new List<SlotStatuses>();
        foreach (GameObject e in column)
        {
            status_list.Add(e.GetComponent<SlotData>().slotStatus);
        }
        byte num_unfilled = (byte)(status_list.Where(status => status.Equals(SlotStatuses.Unfilled)).ToList<SlotStatuses>().Count);
        if (num_unfilled > 0)
        {
            return false;
        }
        else
        {
            return true;
        }

    }

    public void GetAvailableSlot(sbyte requested_col)
    {
        if (IsBoardFull())
        {
            if (gameMode == GameMode.PvAI || gameMode == GameMode.PvP || gameMode == GameMode.RvAI || gameMode == GameMode.AIvAI)
            {
                gameFinished = true;
                latest_winner = SlotStatuses.Unfilled;

                if (gameMode == GameMode.AIvAI)
                {
                    redAgent.UpdateReward();
                    yellowAgent.UpdateReward();
                    StartGame();
                }

                if (gameMode == GameMode.RvAI)
                {
                    redAgent.UpdateReward();
                    StartGame();
                }
                else if (gameMode == GameMode.PvAI) 
                {
                    transform.parent.Find("restart_text").gameObject.SetActive(true);
                    redAgent.UpdateReward();
                }
                return;
            }
        }

        else
        {
            List<GameObject> valid_slots = new List<GameObject>();
            foreach (GameObject s in slots)
            {
                if (s.GetComponent<SlotData>().pos[0] == requested_col)
                {
                    if (s.GetComponent<SlotData>().slotStatus == SlotStatuses.Unfilled)
                    {
                        valid_slots.Add(s);
                    }
                }
            }
            if (!IsColumnFull(valid_slots))
            {
                valid_slots[0].GetComponent<SlotData>().UpdateSlotStatus(current_turn);
                if (CheckWin(current_turn))
                {
                    if (gameMode == GameMode.AIvAI)
                    {
                        yellowAgent.UpdateReward();
                        redAgent.UpdateReward();
                        StartGame();
                    }
                    else if (gameMode == GameMode.RvAI)
                    {
                        redAgent.UpdateReward();
                        StartGame();
                    }
                    else if (gameMode == GameMode.PvAI)
                    {
                        redAgent.UpdateReward();
                    }
                    
                };
            }

        }
    }

    public List<int> IDToColRow(byte id)
    {
        return new List<int>() { (id + 1) % board_dims[1], (id + 1) % board_dims[0] };
    }

    public byte ColRowToID(List<UInt16> colRow)
    {
        return (byte)(colRow[0] + (colRow[1] * board_dims[0]));
    }

    public void CreateSlots()
    {
        board_matrix = new int[board_dims[1], board_dims[0]];
        //DisplayMatrix(board_matrix);

        //DebugList(IDToColRow(7));

        GameObject slot_prefab = Resources.Load<GameObject>("Prefabs/Slot");
        float slot_size = slot_prefab.transform.localScale.x;

        float left_margin = 0f;
        float top_margin = 0f;

        float size_to_padding_ratio = 0.6f;

        float horizontal_padding = slot_size * size_to_padding_ratio;
        float vertical_padding = slot_size * size_to_padding_ratio;

        float total_width = board_dims[0] * (slot_size + horizontal_padding);
        float total_height = board_dims[1] * (slot_size + vertical_padding);

        left_margin = transform.position.x - total_width / 2 + (slot_size / 2);
        top_margin = transform.position.y - total_height / 2 + (slot_size / 2);
        UInt16 num_slots = 0;

        for (int row = 0; row < board_dims[1]; row++)
        {
            for (int col = 0; col < board_dims[0]; col++)
            {
                GameObject new_slot = GameObject.Instantiate(slot_prefab);

                float x_pos = left_margin + col * (slot_size + horizontal_padding);
                col_positions[col] = x_pos;
                float y_pos = top_margin + row * (slot_size + vertical_padding);

                new_slot.transform.localPosition = new Vector2(x_pos, y_pos);
                new_slot.GetComponent<SlotData>().gameManagerObj = gameObject;
                new_slot.transform.parent = gameObject.transform;
                new_slot.GetComponent<SlotData>().pos = new List<int> { col, (board_dims[1] - row) - 1 };
                new_slot.GetComponent<SlotData>().slotID = num_slots;
                slots.Add(new_slot);
                num_slots++;
            }
        }
    }

    public void InitialiseColourData()
    {
        string unfilled_colour_hex = "#7DD1D1";
        string yellow_colour_hex = "#FFF164";
        string red_colour_hex = "#FF5940";

        if (ColorUtility.TryParseHtmlString(unfilled_colour_hex, out Color colour))
        {
            colourData.Add(SlotStatuses.Unfilled.ToString(), colour);
        }

        if (ColorUtility.TryParseHtmlString(yellow_colour_hex, out colour))
        {
            colourData.Add(SlotStatuses.Yellow.ToString(), colour);
        }

        if (ColorUtility.TryParseHtmlString(red_colour_hex, out colour))
        {
            colourData.Add(SlotStatuses.Red.ToString(), colour);
        }
    }

    void InitialisePointer()
    {
        GameObject pointer_prefab = Resources.Load<GameObject>("Prefabs/Pointer");
        pointer = GameObject.Instantiate(pointer_prefab);
        pointer.transform.localPosition = new Vector2(col_positions[(board_dims[0] / 2) - 1], board_bounds.extents.y);
        pointer.transform.parent = gameObject.transform;
        pointer.GetComponent<PointerData>().col_positions = col_positions;
        pointer.GetComponent<PointerData>().selected_col = (byte)((board_dims[0] / 2) - 1);
        pointer.GetComponent<PointerData>().n_cols = board_dims[0];
        pointer.GetComponent<PointerData>().gameManager = gameObject;
        pointer.GetComponent<PointerData>().status = current_turn;
        pointer.GetComponent<SpriteRenderer>().color = colourData[current_turn.ToString()];
    }

    sbyte CheckIndex(KeyCode key)
    {
        for (int i = 0; i < keyCode_nums.Length; i++)
        {
            if (key == keyCode_nums[i])
            {
                return (sbyte)i;
            }
        }
        return -1;
    }

    public void StartGame()
    {
        gameFinished = false;

        foreach (Transform t in transform)
        {
            GameObject.Destroy(t.gameObject);
        }

        if (gameMode == GameMode.RvAI || gameMode == GameMode.AIvAI || gameMode == GameMode.PvAI)
        {
            if(gameMode == GameMode.AIvAI)
            {
                yellowAgent.SetReward(0);
            }
            redAgent.SetReward(0);
        }

        slots.Clear();
        CreateSlots();
        InitialiseTurn();
        InitialisePointer();
        transform.parent.GetComponentInChildren<WinTextManager>(true).gameObject.SetActive(false);

        if(gameMode == GameMode.RvAI && !getAgentFromStatus(ai_colour).plays_second)
        {
            getAgentFromStatus(ai_colour).RequestDecision();
        }

        if(gameMode == GameMode.RvAI && getAgentFromStatus(ai_colour).plays_second)
        {
            PlayRandomTurn();
        }
        if(gameMode == GameMode.PvAI)
        {
            turn_played = false;
        }
    }

    /*
    public override void OnEpisodeBegin()
    {
        if (gameMode == GameMode.PvAI || gameMode == GameMode.RvAI)
        {
            StartGame();
        }
    }*/

    public void PlayRandomTurn()
    {
        int selected_column;
        if (!gameFinished)
        {
            List<int> available_cols = GetAvailableColumns();
            if (available_cols.Count > 1) { selected_column = random.Next(0, available_cols.Count); PlayTurn(available_cols[selected_column]); }
            else {PlayTurn(0); }
            
            turn_played = true;
        }
        if (gameFinished)
        {
            redAgent.SetReward(GetReward(latest_winner, SlotStatuses.Red));
            redAgent.EndEpisode();
        }
    }

    private void Awake()
    {
        //random = new System.Random(debug_seed);
        random = new System.Random();

        col_positions = new List<float>(new float[board_dims[0]]);
        board_bounds = gameObject.GetComponent<SpriteRenderer>().bounds;
    }

    public void Start()
    {
        keyCode_nums = new KeyCode[] {
            KeyCode.Alpha1,
            KeyCode.Alpha2,
            KeyCode.Alpha3,
            KeyCode.Alpha4,
            KeyCode.Alpha5,
            KeyCode.Alpha6,
            KeyCode.Alpha7,
            KeyCode.Alpha8,
            KeyCode.Alpha9,
            KeyCode.Alpha0
        };

        scores = new Dictionary<SlotStatuses, ulong>() {
            {SlotStatuses.Yellow,0},
            {SlotStatuses.Red,0}
        };

        if (gameMode == GameMode.RvAI)
        {
            turn_played = true;
            randomAgent.SetActive(true);
            yellowAgent.gameObject.SetActive(false);
        }
        else if (gameMode == GameMode.AIvAI)
        {
            randomAgent.SetActive(false);
            yellowAgent.gameObject.SetActive(true);
            yellowAgent.GetComponent<AgentManager>().DoEnable();
        }

        else if (gameMode == GameMode.PvAI)
        {
            randomAgent.gameObject.SetActive(false);
            playerAgent.gameObject.SetActive(true);
            playerAgent.GetComponent<PlayerManager>().DoEnable(this);
        }

        redAgent.GetComponent<AgentManager>().DoEnable();

        InitialiseColourData();
        StartGame();
    }

    private KeyCode GetKeyPressed()
    {
        foreach (KeyCode keyCode in System.Enum.GetValues(typeof(KeyCode)))
        {
            if (Input.GetKeyDown(keyCode))
            {
                return keyCode;
            }
        }
        return KeyCode.None;
    }

    public void PlayTurn(int selected_column)
    {

        GetAvailableSlot((sbyte)selected_column);
        current_turn = ToggleTurn(current_turn);
        if (gameMode == GameMode.PvP)
        {
            pointer.GetComponent<PointerData>().SetStatus(current_turn);
        }
        if (gameMode == GameMode.AIvAI)
        {
            SwitchAITurn();
        }

        if (gameMode == GameMode.RvAI)
        {
            if(current_turn == ai_colour)
            {
                redAgent.RequestDecision();
            }
            else if (current_turn == ToggleTurn(ai_colour))
            {
                PlayRandomTurn();
            }
        }
        else if (gameMode == GameMode.PvAI)
        {
            if (current_turn == ai_colour)
            {
                redAgent.RequestDecision();
            }
        }
    }

    public float GetReward(SlotStatuses winner, SlotStatuses check_winner)
    {
        if (winner == check_winner)
        {
            return AgentConstants.winReward;
        }
        else if (winner == ToggleTurn(check_winner))
        {
            return AgentConstants.loseReward;
        }
        else
        {
            return AgentConstants.tieReward;
        }
    }

    public void PlayerPlayTurn()
    {
        int selected_column;
        selected_column = (board_dims[0] / 2) - 1;
        sbyte key_pressed = (sbyte)CheckIndex(GetKeyPressed());
        pointer.GetComponent<PointerData>().UpdatePosition(key_pressed);
        if (Input.GetKeyDown(KeyCode.Return))
        {
            if (!gameFinished)
            {
                selected_column = pointer.GetComponent<PointerData>().selected_col;
                PlayTurn(selected_column);
                turn_played = true;
            }
            else if (gameFinished)
            {
                if (gameMode != GameMode.PvAI)
                {
                    transform.parent.Find("restart_text").gameObject.SetActive(false);
                    StartGame();
                }
                else if (gameMode == GameMode.PvAI)
                {
                    transform.parent.Find("restart_text").gameObject.SetActive(false);
                    redAgent.SetReward(GetReward(latest_winner, SlotStatuses.Red));
                    redAgent.EndEpisode();
                }
            }
        }
    }

    private void Update()
    {

        /*
        if (gameMode == GameMode.PvP || (gameMode == GameMode.PvAI && !turn_played))
        {



        }*/

    }

}
