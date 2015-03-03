import logging
import argparse
import sys
import psycopg2

# Set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)
logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect("dbname='snippets' user='action' host='localhost'")
logging.debug("Database connection established.")

def catalog():
    """print the table"""
    logging.info("printing the table snippets of the database snippets")
    cursor = connection.cursor()
    command = "select keyword, message from snippets"
    cursor.execute(command)
    rows_list = cursor.fetchall()
    connection.commit()
    return rows_list
    
def put(name, snippet):
    """Store a snippet with an associated name."""
    logging.info("Storing snippet in Snippets table")
    cursor = connection.cursor()
    try:
      command = "insert into snippets (keyword, message) values (%s, %s)"
      cursor.execute (command, (name,snippet))
    except psycopg2.IntegrityError as e:
      connection.rollback()
      command = "update snippets set message = %s where keyword = %s"
      cursor.execute (command, (snippet, name))
    connection.commit()
    logging.info("New snippet stored in snippets table")
    return name, snippet
  
def get(name):
    """Retrieve the snippet with a given name."""
    logging.info("Searching for snippet {!r}".format(name))
    cursor = connection.cursor()
    command = "select keyword, message from snippets where keyword=%s"
    cursor.execute(command, (name,))
    row_tuple = cursor.fetchone()
    connection.commit()
    try:
      keyword, message = row_tuple
    except:
      message = None
    logging.info("Retrieval finished for snippet {!r}".format(name))  
    return message

def delete(name):
    """Delete a row in the table"""
    logging.info("Deleting a row in the table")
    cursor = connection.cursor()
    command = "delete from snippets where keyword=%s"
    cursor.execute(command, (name,))
    connection.commit()
    logging.info("Deleted the row with keyword {!r}".format(name))
    return name
  
  
def main():
    """Main function"""
    logging.info("Constructing parser")
    parser = argparse.ArgumentParser(description="Store and retrieve snippets of text")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Subparser for the catalog command
    logging.debug("Constructing catalog subparser")
    catalog_parser = subparsers.add_parser("catalog", help="Prints the table")

    # Subparser for the put command
    logging.debug("Constructing put subparser")
    put_parser = subparsers.add_parser("put", help="Store a snippet")
    put_parser.add_argument("name", help="The name of the snippet to add to the table")
    put_parser.add_argument("snippet", help="The snippet text")


    # Subparser for the get command
    logging.debug("Constructing get subparser")
    get_parser = subparsers.add_parser("get", help="Retrieve a snippet")
    get_parser.add_argument("name", help="The name of the snippet to retrieve")
    
    # Subparser for the delete command
    logging.debug("Constructing delete subparser")
    delete_parser = subparsers.add_parser("delete", help="Deletes a row in the table")
    delete_parser.add_argument("name", help="The name of the snippet to delete")
    
    # Parse arguments and convert parsed arguments from Namespace to dictionary
    arguments = parser.parse_args(sys.argv[1:])
    arguments = vars(arguments)
    command = arguments.pop("command") #get rid of the first item in the dict which is put or get etc...
    

    if command == "catalog":
      rows = catalog()
      for row in rows:
        keyword, message = row
        print "{!r} = {!r}".format(keyword, message)
    elif command == "delete":
      name = delete(**arguments)
      print "The table no longer has row with keyword {!r}".format(name)
    elif command == "put":
      name, snippet = put(**arguments)  #unpack the arguments i.e. turn the dict k,v's into keyword arguments
      print "Stored {!r} as {!r}".format(snippet, name)
    elif command == "get":
      snippet = get(**arguments)
      if snippet:
        print "Retrieved snippet: {!r}".format(snippet)
      else:
        #if no snippet is found the get function still executes
        #without an error but returns None
        print "No snippets found"


      
if __name__ == "__main__":
    main() 
    
    
    
    
    