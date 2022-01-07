import React from "react";
import AdminLoginForm from "../components/AdminLoginForm";
import { Flex, Stack, Image } from "@chakra-ui/react";
import background from "../images/background.png";
import ColourModeToggle from "../components/ColourModeToggle";

const AdminLoginPage = () => {
  return (
    <Stack minH={"100vh"} direction={{ base: "column", md: "row" }}>
      <Flex flex={2}>
        <Image
          alt={"Cool robotics background image"}
          objectFit={"cover"}
          src={background}
        />
      </Flex>
      <Flex p={8} flex={1} align={"center"} justify={"center"}>
        <Stack spacing={4} w={"full"} maxW={"md"}>
          <AdminLoginForm />
        </Stack>
      </Flex>
      <ColourModeToggle />
    </Stack>
  );
};

export default AdminLoginPage;
