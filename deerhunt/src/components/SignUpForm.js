import React from "react";
import { useForm } from "react-hook-form";
import {
  Flex,
  Box,
  Heading,
  FormControl,
  FormLabel,
  Input,
  Button,
  Link,
  Text,
} from "@chakra-ui/react";
import { useHistory } from "react-router-dom";
import { useStateValue } from "../statemanager/StateProvider";
import axios from "../config/config";



export default function SignUpForm(props) {
  const [{ }, dispatch] =useStateValue();
  const setError = props.setError;
  const {
    handleSubmit,
    register,
    formState: { isSubmitting },
  } = useForm();
  const history = useHistory();
  async function SignUp(values) {
    var form = new FormData();
    console.log(axios.defaults.baseURL);
    form.append("email", values.email);
    form.append("password", values.password);
    await axios
      .post("api/user", form)
      .then((response) => {
        dispatch({
          type: "SIGNED_UP",
        });
        history.push("/login");
      })
      .catch((error) => {

        setError(error.response.data.message);

        dispatch({
          type: "SignUpFail",

        });
      });
  }

  return (
    <Flex
      minHeight="100vh"
      width="full"
      justifyContent="center"
      alignItems="center"
    >
      <Box>
        <Box
          borderWidth={1}
          px={8}
          py={8}
          borderRadius={4}
          boxShadow="lg"
          width="full"
          maxWidth="500px"
          bg="gray.300"
        >
          <Box textAlign="center" mb={4}>
            <Heading size="md">Signup for Deerhunt</Heading>
          </Box>
          <Box>
            <form onSubmit={handleSubmit(SignUp)}>
              <FormControl>
                <FormLabel>Email</FormLabel>
                <Input
                  type="email"
                  placeholder="Enter Your Email"
                  {...register("email", {
                    required: "This is required",
                  })}
                />
              </FormControl>
              <FormControl mt={4}>
                <FormLabel>Password</FormLabel>
                <Input
                  type="password"
                  placeholder="Enter Your Password"
                  {...register("password", {
                    required: "This is required",
                    minLength: {
                      value: 8,
                      message: "Minimum length should be 4",
                    },
                  })}
                />
              </FormControl>
              <Box my={4}>
                <Button width="full" isLoading={isSubmitting} type="submit">
                  Sign Up
                </Button>
              </Box>
              <Box textAlign="center">
                <Link
                  onClick={() => {
                    window.location.href = "/login";
                  }}
                >
                  <Text>I already have an account</Text>
                </Link>
              </Box>
            </form>
          </Box>
        </Box>
      </Box>
    </Flex>
  );
}

