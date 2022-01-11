import React, { useEffect, useState } from "react";
import {
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableCaption,
  Button,
} from "@chakra-ui/react";
import axios from "../config/config.js";

const Leaderboard = (props) => {
  const [leaderboard, setLeaderboard] = useState([]);
  const [myTeam, setMyTeam] = useState("");

  useEffect(() => {
    let form = new FormData();
    form.append("name", props.event);
    axios
      .post("/api/user/team", form)
      .then((response) => {
        setMyTeam(response.data);
      })
      .catch();
    axios
      .get("/api/leaderboard", {
        params: { name: props.event },
      })
      .then((response) => {
        setLeaderboard(response.data);
      })
      .catch();
  }, []);

  const getChallengeFunction = (team, opponent) => {
    return () => {
      var form = new FormData();
      form.append("name", props.event);
      form.append("team1_id", team._id);
      form.append("team2_id", opponent._id);
      axios
        .post("/api/requests", form)
        .then((response) => console.log(response));
    };
  };

  return (
    <Table>
      <TableCaption>
        Press challenge to play a team and overtake them on the leaderboard!
      </TableCaption>
      <Thead>
        <Tr>
          <Th>#</Th>
          <Th>Team</Th>
          <Th />
        </Tr>
      </Thead>
      <Tbody>
        {leaderboard.map((team, index) => (
          <Tr key={index}>
            <Td>{index + 1}</Td>
            <Td>{team.name}</Td>
            <Td>
              {index < leaderboard.map((e) => e.name).indexOf(myTeam.name) ? (
                <Button onClick={getChallengeFunction(myTeam, team)}>
                  Challenge
                </Button>
              ) : null}
            </Td>
          </Tr>
        ))}
      </Tbody>
    </Table>
  );
};

export default Leaderboard;
